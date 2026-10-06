"""
DAG 01: Dataset Preprocessor and CSV to MySQL
Reads StudentPerformanceFactors.csv, preprocesses the data,
saves preprocessing artifacts, and stores data into MySQL.
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os

DEFAULT_ARGS = {
    "owner": "mlops",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

DATASET_PATH = "/opt/airflow/dataset/raw/StudentPerformanceFactors.csv"
ARTIFACTS_DIR = "/opt/airflow/artifacts"
PREPROCESSING_DIR = f"{ARTIFACTS_DIR}/preprocessing"

MYSQL_HOST = os.getenv("MYSQL_HOST", "mysql")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_DB = os.getenv("MYSQL_DATABASE", "mlops_db")
MYSQL_USER = os.getenv("MYSQL_USER", "mlops_user")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "mlops_password")

CATEGORICAL_ORDINAL = {
    "Parental_Involvement": ["Low", "Medium", "High"],
    "Access_to_Resources": ["Low", "Medium", "High"],
    "Motivation_Level": ["Low", "Medium", "High"],
    "Family_Income": ["Low", "Medium", "High"],
    "Teacher_Quality": ["Low", "Medium", "High"],
    "Parental_Education_Level": ["High School", "College", "Postgraduate"],
    "Distance_from_Home": ["Near", "Moderate", "Far"],
    "Peer_Influence": ["Negative", "Neutral", "Positive"],
}
CATEGORICAL_BINARY = [
    "Extracurricular_Activities",
    "Internet_Access",
    "Learning_Disabilities",
    "Gender",
    "School_Type",
]
NUMERICAL_FEATURES = [
    "Hours_Studied", "Attendance", "Sleep_Hours",
    "Previous_Scores", "Tutoring_Sessions", "Physical_Activity",
]
TARGET_COLUMN = "Exam_Score"


def load_and_validate():
    import pandas as pd
    df = pd.read_csv(DATASET_PATH)
    print(f"Loaded dataset: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"Columns: {list(df.columns)}")
    missing = df.isnull().sum()
    print(f"Missing values:\n{missing[missing > 0]}")
    assert TARGET_COLUMN in df.columns, f"Target column {TARGET_COLUMN} not found"
    return df.shape


def preprocess_and_save():
    import pandas as pd
    import numpy as np
    import joblib
    from sklearn.preprocessing import StandardScaler, OrdinalEncoder, LabelEncoder

    os.makedirs(PREPROCESSING_DIR, exist_ok=True)

    df = pd.read_csv(DATASET_PATH)

    # Fill missing values
    for col in NUMERICAL_FEATURES + [TARGET_COLUMN]:
        df[col] = df[col].fillna(df[col].median())
    for col in CATEGORICAL_BINARY + list(CATEGORICAL_ORDINAL.keys()):
        df[col] = df[col].fillna(df[col].mode()[0])

    # Ordinal encoding for ordinal categoricals
    ordinal_encoders = {}
    for col, categories in CATEGORICAL_ORDINAL.items():
        enc = OrdinalEncoder(categories=[categories], handle_unknown="use_encoded_value", unknown_value=-1)
        df[col] = enc.fit_transform(df[[col]])
        ordinal_encoders[col] = enc
    joblib.dump(ordinal_encoders, f"{PREPROCESSING_DIR}/ordinal_encoders.joblib")

    # Label encoding for binary categoricals
    label_encoders = {}
    for col in CATEGORICAL_BINARY:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        label_encoders[col] = le
    joblib.dump(label_encoders, f"{PREPROCESSING_DIR}/label_encoders.joblib")

    # Scale numerical features
    scaler = StandardScaler()
    df[NUMERICAL_FEATURES] = scaler.fit_transform(df[NUMERICAL_FEATURES])
    joblib.dump(scaler, f"{PREPROCESSING_DIR}/numerical_scaler.joblib")

    # Save feature names and metadata
    feature_cols = NUMERICAL_FEATURES + CATEGORICAL_BINARY + list(CATEGORICAL_ORDINAL.keys())
    metadata = {
        "feature_columns": feature_cols,
        "target_column": TARGET_COLUMN,
        "numerical_features": NUMERICAL_FEATURES,
        "categorical_binary": CATEGORICAL_BINARY,
        "categorical_ordinal": list(CATEGORICAL_ORDINAL.keys()),
        "ordinal_categories": CATEGORICAL_ORDINAL,
        "n_samples": len(df),
        "n_features": len(feature_cols),
    }
    import json
    with open(f"{PREPROCESSING_DIR}/metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    df.to_csv(f"{PREPROCESSING_DIR}/preprocessed_data.csv", index=False)
    print(f"Preprocessed data saved: {df.shape}")
    print(f"Artifacts saved to {PREPROCESSING_DIR}")


def store_to_mysql():
    import pandas as pd
    import sqlalchemy

    df = pd.read_csv(f"{PREPROCESSING_DIR}/preprocessed_data.csv")

    connection_str = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
        f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    )
    engine = sqlalchemy.create_engine(connection_str)

    with engine.begin() as conn:
        conn.execute(sqlalchemy.text("CREATE DATABASE IF NOT EXISTS mlops_db"))

    df.to_sql(
        "student_performance",
        engine,
        if_exists="replace",
        index=False,
        chunksize=500,
    )
    print(f"Stored {len(df)} rows into MySQL table 'student_performance'")

    # Also store raw data
    raw_df = pd.read_csv(DATASET_PATH)
    raw_df.to_sql(
        "student_performance_raw",
        engine,
        if_exists="replace",
        index=False,
        chunksize=500,
    )
    print(f"Stored {len(raw_df)} rows into MySQL table 'student_performance_raw'")
    engine.dispose()


with DAG(
    dag_id="01_dataset_preprocessor_and_csv_to_mysql",
    default_args=DEFAULT_ARGS,
    description="Preprocess StudentPerformanceFactors CSV and load into MySQL",
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["preprocessing", "data-ingestion"],
) as dag:

    task_load_validate = PythonOperator(
        task_id="load_and_validate_dataset",
        python_callable=load_and_validate,
    )

    task_preprocess = PythonOperator(
        task_id="preprocess_and_save_artifacts",
        python_callable=preprocess_and_save,
    )

    task_store_mysql = PythonOperator(
        task_id="store_to_mysql",
        python_callable=store_to_mysql,
    )

    task_load_validate >> task_preprocess >> task_store_mysql
