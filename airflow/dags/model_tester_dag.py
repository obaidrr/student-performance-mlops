"""
DAG 05: Model Tester
Runs comprehensive evaluation tests over all trained/tuned models,
generates performance metrics, and stores results in artifacts/.
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
METRICS_DIR = f"{ARTIFACTS_DIR}/metrics"


def evaluate_trained_models():
    import numpy as np
    import json
    import joblib
    import glob
    from sklearn.metrics import (
        mean_squared_error, mean_absolute_error, r2_score,
        explained_variance_score, max_error,
    )

    os.makedirs(METRICS_DIR, exist_ok=True)

    X_test = np.load(f"{MODELS_DIR}/X_test.npy")
    y_test = np.load(f"{MODELS_DIR}/y_test.npy")

    model_files = glob.glob(f"{MODELS_DIR}/*_trained.joblib") + \
                  glob.glob(f"{MODELS_DIR}/*_baseline.joblib")

    all_metrics = {}

    for model_path in model_files:
        model_name = os.path.basename(model_path).replace(".joblib", "")
        model = joblib.load(model_path)
        y_pred = model.predict(X_test)

        metrics = {
            "rmse": float(np.sqrt(mean_squared_error(y_test, y_pred))),
            "mae": float(mean_absolute_error(y_test, y_pred)),
            "r2": float(r2_score(y_test, y_pred)),
            "explained_variance": float(explained_variance_score(y_test, y_pred)),
            "max_error": float(max_error(y_test, y_pred)),
            "mean_error": float(np.mean(y_test - y_pred)),
        }
        all_metrics[model_name] = metrics
        print(f"{model_name}: R2={metrics['r2']:.4f}, RMSE={metrics['rmse']:.4f}")

    with open(f"{METRICS_DIR}/trained_models_metrics.json", "w") as f:
        json.dump(all_metrics, f, indent=2)

    print(f"\nEvaluated {len(all_metrics)} trained models")


def evaluate_tuned_models():
    import numpy as np
    import json
    import joblib
    import glob
    from sklearn.metrics import (
        mean_squared_error, mean_absolute_error, r2_score,
        explained_variance_score, max_error,
    )

    X_test = np.load(f"{MODELS_DIR}/X_test.npy")
    y_test = np.load(f"{MODELS_DIR}/y_test.npy")

    model_files = glob.glob(f"{TUNED_DIR}/*_tuned.joblib")
    all_metrics = {}

    for model_path in model_files:
        model_name = os.path.basename(model_path).replace(".joblib", "")
        model = joblib.load(model_path)
        y_pred = model.predict(X_test)

        metrics = {
            "rmse": float(np.sqrt(mean_squared_error(y_test, y_pred))),
            "mae": float(mean_absolute_error(y_test, y_pred)),
            "r2": float(r2_score(y_test, y_pred)),
            "explained_variance": float(explained_variance_score(y_test, y_pred)),
            "max_error": float(max_error(y_test, y_pred)),
            "mean_error": float(np.mean(y_test - y_pred)),
        }
        all_metrics[model_name] = metrics
        print(f"{model_name}: R2={metrics['r2']:.4f}, RMSE={metrics['rmse']:.4f}")

    with open(f"{METRICS_DIR}/tuned_models_metrics.json", "w") as f:
        json.dump(all_metrics, f, indent=2)

    print(f"\nEvaluated {len(all_metrics)} tuned models")


def run_prediction_sanity_checks():
    import numpy as np
    import json
    import joblib

    X_test = np.load(f"{MODELS_DIR}/X_test.npy")
    y_test = np.load(f"{MODELS_DIR}/y_test.npy")

    best_model_info_path = f"{TUNED_DIR}/best_tuned_model_info.json"
    if not os.path.exists(best_model_info_path):
        print("No tuned model info found, using trained models")
        best_model_path = f"{MODELS_DIR}/GradientBoosting_trained.joblib"
        if not os.path.exists(best_model_path):
            import glob
            trained = glob.glob(f"{MODELS_DIR}/*_trained.joblib")
            best_model_path = trained[0] if trained else None
    else:
        with open(best_model_info_path) as f:
            info = json.load(f)
        best_model_path = info["model_file"]

    if not best_model_path or not os.path.exists(best_model_path):
        print("No model found for sanity check")
        return

    model = joblib.load(best_model_path)
    sample_indices = np.random.choice(len(X_test), size=10, replace=False)
    X_sample = X_test[sample_indices]
    y_actual = y_test[sample_indices]
    y_pred = model.predict(X_sample)

    checks = []
    all_passed = True
    for i, (actual, pred) in enumerate(zip(y_actual, y_pred)):
        error = abs(actual - pred)
        passed = error < 20  # within 20 score points is reasonable
        checks.append({
            "sample": int(sample_indices[i]),
            "actual": float(actual),
            "predicted": float(pred),
            "absolute_error": float(error),
            "passed": passed,
        })
        if not passed:
            all_passed = False

    sanity_results = {
        "model_path": best_model_path,
        "n_checks": len(checks),
        "all_passed": all_passed,
        "pass_rate": sum(c["passed"] for c in checks) / len(checks),
        "checks": checks,
    }

    with open(f"{METRICS_DIR}/sanity_checks.json", "w") as f:
        json.dump(sanity_results, f, indent=2)

    print(f"Sanity checks: {sum(c['passed'] for c in checks)}/{len(checks)} passed")
    print(f"Pass rate: {sanity_results['pass_rate']:.1%}")


def generate_final_metrics_report():
    import json
    import glob

    all_metrics = {}

    for mfile in glob.glob(f"{METRICS_DIR}/*.json"):
        if "sanity" not in mfile:
            with open(mfile) as f:
                data = json.load(f)
            all_metrics.update(data)

    # Find champion model (highest R2)
    if all_metrics:
        champion = max(all_metrics, key=lambda k: all_metrics[k].get("r2", -999))
        champion_metrics = all_metrics[champion]
    else:
        champion = "unknown"
        champion_metrics = {}

    report = {
        "champion_model": champion,
        "champion_metrics": champion_metrics,
        "all_models": all_metrics,
        "evaluation_date": datetime.utcnow().isoformat(),
    }

    with open(f"{METRICS_DIR}/final_metrics_report.json", "w") as f:
        json.dump(report, f, indent=2)

    # Also write a summary to artifacts root for the API to pick up
    with open(f"{ARTIFACTS_DIR}/model_metrics.json", "w") as f:
        json.dump(report, f, indent=2)

    print(f"\nChampion model: {champion}")
    if champion_metrics:
        print(f"  R2:   {champion_metrics.get('r2', 'N/A'):.4f}")
        print(f"  RMSE: {champion_metrics.get('rmse', 'N/A'):.4f}")
        print(f"  MAE:  {champion_metrics.get('mae', 'N/A'):.4f}")


with DAG(
    dag_id="05_model_tester",
    default_args=DEFAULT_ARGS,
    description="Comprehensive evaluation of all trained and tuned models",
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["model-testing", "evaluation"],
) as dag:

    task_eval_trained = PythonOperator(
        task_id="evaluate_trained_models",
        python_callable=evaluate_trained_models,
    )

    task_eval_tuned = PythonOperator(
        task_id="evaluate_tuned_models",
        python_callable=evaluate_tuned_models,
    )

    task_sanity = PythonOperator(
        task_id="run_prediction_sanity_checks",
        python_callable=run_prediction_sanity_checks,
    )

    task_report = PythonOperator(
        task_id="generate_final_metrics_report",
        python_callable=generate_final_metrics_report,
    )

    [task_eval_trained, task_eval_tuned] >> task_sanity >> task_report
