"""
DAG 02: Model Selector
Loads preprocessed data from MySQL, tests multiple supervised regression
models, and saves comparison results to artifacts/.
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

ARTIFACTS_DIR = "/opt/airflow/artifacts"
PREPROCESSING_DIR = f"{ARTIFACTS_DIR}/preprocessing"
MODELS_DIR = f"{ARTIFACTS_DIR}/models"

MYSQL_HOST = os.getenv("MYSQL_HOST", "mysql")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_DB = os.getenv("MYSQL_DATABASE", "mlops_db")
MYSQL_USER = os.getenv("MYSQL_USER", "mlops_user")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "mlops_password")


def load_data_from_mysql():
    import pandas as pd
    import sqlalchemy

    connection_str = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
        f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    )
    engine = sqlalchemy.create_engine(connection_str)
    df = pd.read_sql("SELECT * FROM student_performance", engine)
    engine.dispose()
    print(f"Loaded {len(df)} rows from MySQL")
    df.to_csv(f"{PREPROCESSING_DIR}/data_from_db.csv", index=False)


def evaluate_candidate_models():
    import pandas as pd
    import numpy as np
    import json
    import warnings
    from sklearn.model_selection import cross_val_score, train_test_split
    from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
    from sklearn.ensemble import (
        RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor
    )
    from sklearn.svm import SVR
    from sklearn.tree import DecisionTreeRegressor
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

    warnings.filterwarnings("ignore")
    os.makedirs(MODELS_DIR, exist_ok=True)

    df = pd.read_csv(f"{PREPROCESSING_DIR}/data_from_db.csv")

    with open(f"{PREPROCESSING_DIR}/metadata.json") as f:
        metadata = json.load(f)

    feature_cols = metadata["feature_columns"]
    target_col = metadata["target_column"]

    X = df[feature_cols].values
    y = df[target_col].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    candidates = {
        "LinearRegression": LinearRegression(),
        "Ridge": Ridge(alpha=1.0),
        "Lasso": Lasso(alpha=0.1),
        "ElasticNet": ElasticNet(alpha=0.1, l1_ratio=0.5),
        "DecisionTree": DecisionTreeRegressor(max_depth=10, random_state=42),
        "RandomForest": RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1),
        "GradientBoosting": GradientBoostingRegressor(n_estimators=100, random_state=42),
        "ExtraTrees": ExtraTreesRegressor(n_estimators=100, random_state=42, n_jobs=-1),
    }

    results = []
    for name, model in candidates.items():
        print(f"Evaluating {name}...")
        cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring="r2", n_jobs=-1)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
        mae = float(mean_absolute_error(y_test, y_pred))
        r2 = float(r2_score(y_test, y_pred))
        cv_mean = float(cv_scores.mean())
        cv_std = float(cv_scores.std())
        results.append({
            "model": name,
            "rmse": rmse,
            "mae": mae,
            "r2": r2,
            "cv_r2_mean": cv_mean,
            "cv_r2_std": cv_std,
        })
        print(f"  RMSE: {rmse:.4f}, MAE: {mae:.4f}, R2: {r2:.4f}, CV-R2: {cv_mean:.4f}±{cv_std:.4f}")

    results.sort(key=lambda x: x["r2"], reverse=True)

    comparison = {
        "results": results,
        "best_model": results[0]["model"],
        "top_3_models": [r["model"] for r in results[:3]],
        "problem_type": "regression",
        "target_column": target_col,
        "n_features": len(feature_cols),
        "n_samples": len(df),
    }

    with open(f"{ARTIFACTS_DIR}/model_comparison.json", "w") as f:
        json.dump(comparison, f, indent=2)

    print(f"\nModel Comparison Results:")
    for r in results:
        print(f"  {r['model']}: R2={r['r2']:.4f}, RMSE={r['rmse']:.4f}")
    print(f"\nBest model: {comparison['best_model']}")
    print(f"Top 3 models: {comparison['top_3_models']}")


def summarize_selection():
    import json

    with open(f"{ARTIFACTS_DIR}/model_comparison.json") as f:
        comparison = json.load(f)

    print("=" * 50)
    print("MODEL SELECTION SUMMARY")
    print("=" * 50)
    print(f"Problem type: {comparison['problem_type']}")
    print(f"Best model selected: {comparison['best_model']}")
    print(f"Top 3 models: {comparison['top_3_models']}")
    print("\nFull rankings:")
    for i, r in enumerate(comparison["results"], 1):
        print(f"  {i}. {r['model']} - R2: {r['r2']:.4f}, RMSE: {r['rmse']:.4f}, CV-R2: {r['cv_r2_mean']:.4f}")


with DAG(
    dag_id="02_model_selector",
    default_args=DEFAULT_ARGS,
    description="Evaluate candidate ML models and select the best performers",
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["model-selection"],
) as dag:

    task_load = PythonOperator(
        task_id="load_data_from_mysql",
        python_callable=load_data_from_mysql,
    )

    task_evaluate = PythonOperator(
        task_id="evaluate_candidate_models",
        python_callable=evaluate_candidate_models,
    )

    task_summarize = PythonOperator(
        task_id="summarize_model_selection",
        python_callable=summarize_selection,
    )

    task_load >> task_evaluate >> task_summarize
