"""
DAG 04: Model Tuner
Loads trained models, performs hyperparameter tuning using RandomizedSearchCV,
selects the best tuned model, and saves results to artifacts/.
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
MODELS_DIR = f"{ARTIFACTS_DIR}/models"
TUNED_DIR = f"{ARTIFACTS_DIR}/tuned_models"


def tune_random_forest():
    import numpy as np
    import json
    import joblib
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import RandomizedSearchCV
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

    os.makedirs(TUNED_DIR, exist_ok=True)

    X_train = np.load(f"{MODELS_DIR}/X_train.npy")
    X_test = np.load(f"{MODELS_DIR}/X_test.npy")
    y_train = np.load(f"{MODELS_DIR}/y_train.npy")
    y_test = np.load(f"{MODELS_DIR}/y_test.npy")

    param_dist = {
        "n_estimators": [100, 200, 300, 500],
        "max_depth": [None, 10, 20, 30],
        "min_samples_split": [2, 5, 10],
        "min_samples_leaf": [1, 2, 4],
        "max_features": ["sqrt", "log2", None],
    }

    base_model = RandomForestRegressor(random_state=42, n_jobs=1)
    search = RandomizedSearchCV(
        base_model,
        param_distributions=param_dist,
        n_iter=20,
        cv=5,
        scoring="r2",
        random_state=42,
        n_jobs=1,
        verbose=1,
    )

    print("Tuning RandomForestRegressor...")
    search.fit(X_train, y_train)

    best_model = search.best_estimator_
    y_pred = best_model.predict(X_test)

    result = {
        "model": "RandomForest_tuned",
        "best_params": search.best_params_,
        "cv_best_score": float(search.best_score_),
        "rmse": float(np.sqrt(mean_squared_error(y_test, y_pred))),
        "mae": float(mean_absolute_error(y_test, y_pred)),
        "r2": float(r2_score(y_test, y_pred)),
    }

    joblib.dump(best_model, f"{TUNED_DIR}/RandomForest_tuned.joblib")

    with open(f"{TUNED_DIR}/RandomForest_tuning_results.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"RandomForest tuned — R2: {result['r2']:.4f}, RMSE: {result['rmse']:.4f}")
    print(f"Best params: {search.best_params_}")


def tune_gradient_boosting():
    import numpy as np
    import json
    import joblib
    from sklearn.ensemble import GradientBoostingRegressor
    from sklearn.model_selection import RandomizedSearchCV
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

    X_train = np.load(f"{MODELS_DIR}/X_train.npy")
    X_test = np.load(f"{MODELS_DIR}/X_test.npy")
    y_train = np.load(f"{MODELS_DIR}/y_train.npy")
    y_test = np.load(f"{MODELS_DIR}/y_test.npy")

    param_dist = {
        "n_estimators": [100, 200, 300, 500],
        "learning_rate": [0.01, 0.05, 0.1, 0.2],
        "max_depth": [3, 5, 7, 9],
        "min_samples_split": [2, 5, 10],
        "min_samples_leaf": [1, 2, 4],
        "subsample": [0.7, 0.8, 0.9, 1.0],
    }

    base_model = GradientBoostingRegressor(random_state=42)
    search = RandomizedSearchCV(
        base_model,
        param_distributions=param_dist,
        n_iter=20,
        cv=5,
        scoring="r2",
        random_state=42,
        n_jobs=1,
        verbose=1,
    )

    print("Tuning GradientBoostingRegressor...")
    search.fit(X_train, y_train)

    best_model = search.best_estimator_
    y_pred = best_model.predict(X_test)

    result = {
        "model": "GradientBoosting_tuned",
        "best_params": search.best_params_,
        "cv_best_score": float(search.best_score_),
        "rmse": float(np.sqrt(mean_squared_error(y_test, y_pred))),
        "mae": float(mean_absolute_error(y_test, y_pred)),
        "r2": float(r2_score(y_test, y_pred)),
    }

    joblib.dump(best_model, f"{TUNED_DIR}/GradientBoosting_tuned.joblib")

    with open(f"{TUNED_DIR}/GradientBoosting_tuning_results.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"GradientBoosting tuned — R2: {result['r2']:.4f}, RMSE: {result['rmse']:.4f}")
    print(f"Best params: {search.best_params_}")


def select_best_tuned_model():
    import json
    import joblib
    import shutil

    tuning_files = {
        "RandomForest": f"{TUNED_DIR}/RandomForest_tuning_results.json",
        "GradientBoosting": f"{TUNED_DIR}/GradientBoosting_tuning_results.json",
    }

    results = {}
    for name, path in tuning_files.items():
        if os.path.exists(path):
            with open(path) as f:
                results[name] = json.load(f)

    if not results:
        raise FileNotFoundError("No tuning results found")

    best_name = max(results, key=lambda k: results[k]["r2"])
    best_result = results[best_name]

    # Copy best tuned model as the champion
    src = f"{TUNED_DIR}/{best_name}_tuned.joblib"
    dst = f"{TUNED_DIR}/best_tuned_model.joblib"
    if os.path.exists(src):
        shutil.copy2(src, dst)

    best_model_info = {
        "best_tuned_model": best_name,
        "model_file": dst,
        "metrics": best_result,
        "all_tuned_results": results,
    }

    with open(f"{TUNED_DIR}/best_tuned_model_info.json", "w") as f:
        json.dump(best_model_info, f, indent=2)

    print(f"\nBest tuned model: {best_name}")
    print(f"  R2: {best_result['r2']:.4f}")
    print(f"  RMSE: {best_result['rmse']:.4f}")
    print(f"  MAE: {best_result['mae']:.4f}")


with DAG(
    dag_id="04_model_tuner",
    default_args=DEFAULT_ARGS,
    description="Hyperparameter tuning for top ML models",
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["model-tuning"],
) as dag:

    task_tune_rf = PythonOperator(
        task_id="tune_random_forest",
        python_callable=tune_random_forest,
    )

    task_tune_gb = PythonOperator(
        task_id="tune_gradient_boosting",
        python_callable=tune_gradient_boosting,
    )

    task_select_best = PythonOperator(
        task_id="select_best_tuned_model",
        python_callable=select_best_tuned_model,
    )

    [task_tune_rf, task_tune_gb] >> task_select_best
