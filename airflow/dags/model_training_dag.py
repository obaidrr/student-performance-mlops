"""
DAG 03: Model Training
Trains the top models identified in the model selection phase
on the full training set and saves them to artifacts/models/.
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


def prepare_train_test_split():
    import pandas as pd
    import numpy as np
    import json
    from sklearn.model_selection import train_test_split

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

    np.save(f"{MODELS_DIR}/X_train.npy", X_train)
    np.save(f"{MODELS_DIR}/X_test.npy", X_test)
    np.save(f"{MODELS_DIR}/y_train.npy", y_train)
    np.save(f"{MODELS_DIR}/y_test.npy", y_test)

    split_info = {
        "train_size": len(X_train),
        "test_size": len(X_test),
        "n_features": len(feature_cols),
        "feature_columns": feature_cols,
        "target_column": target_col,
    }
    with open(f"{MODELS_DIR}/split_info.json", "w") as f:
        json.dump(split_info, f, indent=2)

    print(f"Train size: {len(X_train)}, Test size: {len(X_test)}")


def train_best_model():
    import numpy as np
    import json
    import joblib
    from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
    from sklearn.linear_model import LinearRegression, Ridge, ElasticNet
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

    X_train = np.load(f"{MODELS_DIR}/X_train.npy")
    X_test = np.load(f"{MODELS_DIR}/X_test.npy")
    y_train = np.load(f"{MODELS_DIR}/y_train.npy")
    y_test = np.load(f"{MODELS_DIR}/y_test.npy")

    with open(f"{ARTIFACTS_DIR}/model_comparison.json") as f:
        comparison = json.load(f)

    model_registry = {
        "LinearRegression": LinearRegression(),
        "Ridge": Ridge(alpha=1.0),
        "ElasticNet": ElasticNet(random_state=42),
        "RandomForest": RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=1),
        "GradientBoosting": GradientBoostingRegressor(n_estimators=200, random_state=42),
    }

    top_models = comparison.get("top_3_models", [comparison["best_model"]])
    training_results = {}

    for model_name in top_models:
        if model_name not in model_registry:
            print(f"Skipping {model_name} — not in registry")
            continue

        model = model_registry[model_name]
        print(f"Training {model_name}...")
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
        mae = float(mean_absolute_error(y_test, y_pred))
        r2 = float(r2_score(y_test, y_pred))

        model_path = f"{MODELS_DIR}/{model_name}_trained.joblib"
        joblib.dump(model, model_path)

        training_results[model_name] = {
            "rmse": rmse,
            "mae": mae,
            "r2": r2,
            "model_path": model_path,
        }
        print(f"  {model_name} — RMSE: {rmse:.4f}, R2: {r2:.4f} saved to {model_path}")

    with open(f"{MODELS_DIR}/training_results.json", "w") as f:
        json.dump(training_results, f, indent=2)

    print(f"\nTrained {len(training_results)} models.")


def train_baseline_model():
    import numpy as np
    import json
    import joblib
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

    X_train = np.load(f"{MODELS_DIR}/X_train.npy")
    X_test = np.load(f"{MODELS_DIR}/X_test.npy")
    y_train = np.load(f"{MODELS_DIR}/y_train.npy")
    y_test = np.load(f"{MODELS_DIR}/y_test.npy")

    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    baseline = {
        "model": "LinearRegression_baseline",
        "rmse": float(np.sqrt(mean_squared_error(y_test, y_pred))),
        "mae": float(mean_absolute_error(y_test, y_pred)),
        "r2": float(r2_score(y_test, y_pred)),
    }

    joblib.dump(model, f"{MODELS_DIR}/LinearRegression_baseline.joblib")

    with open(f"{MODELS_DIR}/baseline_results.json", "w") as f:
        json.dump(baseline, f, indent=2)

    print(f"Baseline model — RMSE: {baseline['rmse']:.4f}, R2: {baseline['r2']:.4f}")


with DAG(
    dag_id="03_model_training",
    default_args=DEFAULT_ARGS,
    description="Train top selected ML models and save to artifacts",
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["model-training"],
) as dag:

    task_split = PythonOperator(
        task_id="prepare_train_test_split",
        python_callable=prepare_train_test_split,
    )

    task_baseline = PythonOperator(
        task_id="train_baseline_model",
        python_callable=train_baseline_model,
    )

    task_train = PythonOperator(
        task_id="train_best_models",
        python_callable=train_best_model,
    )

    task_split >> task_baseline >> task_train
