"""
DAG 06: Model Extractor
Extracts all trained and tuned models as joblib files into the artifacts/ folder,
generates a manifest, and marks the pipeline as complete.
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
FINAL_MODELS_DIR = f"{ARTIFACTS_DIR}/final_models"


def extract_all_models():
    import glob
    import shutil
    import json

    os.makedirs(FINAL_MODELS_DIR, exist_ok=True)

    extracted = []

    # Copy trained models
    for src in glob.glob(f"{MODELS_DIR}/*.joblib"):
        fname = os.path.basename(src)
        dst = f"{FINAL_MODELS_DIR}/{fname}"
        shutil.copy2(src, dst)
        extracted.append({"source": src, "destination": dst, "type": "trained"})
        print(f"Extracted: {fname}")

    # Copy tuned models
    for src in glob.glob(f"{TUNED_DIR}/*.joblib"):
        fname = os.path.basename(src)
        dst = f"{FINAL_MODELS_DIR}/{fname}"
        shutil.copy2(src, dst)
        extracted.append({"source": src, "destination": dst, "type": "tuned"})
        print(f"Extracted: {fname}")

    with open(f"{FINAL_MODELS_DIR}/extraction_log.json", "w") as f:
        json.dump({"extracted_models": extracted, "count": len(extracted)}, f, indent=2)

    print(f"\nTotal models extracted: {len(extracted)}")


def identify_champion_model():
    import json
    import shutil
    import glob

    metrics_path = f"{ARTIFACTS_DIR}/model_metrics.json"

    if not os.path.exists(metrics_path):
        # Fall back: pick any tuned model
        tuned = glob.glob(f"{TUNED_DIR}/*_tuned.joblib")
        if tuned:
            champion_src = tuned[0]
            champion_name = os.path.basename(champion_src).replace(".joblib", "")
        else:
            trained = glob.glob(f"{MODELS_DIR}/*_trained.joblib")
            champion_src = trained[0] if trained else None
            champion_name = os.path.basename(champion_src).replace(".joblib", "") if champion_src else "unknown"
    else:
        with open(metrics_path) as f:
            metrics = json.load(f)
        champion_name = metrics.get("champion_model", "unknown")
        champion_src = f"{FINAL_MODELS_DIR}/{champion_name}.joblib"
        if not os.path.exists(champion_src):
            # Try with _tuned or _trained suffix variants
            for suffix in ["_tuned", "_trained", "_baseline", ""]:
                candidate = f"{FINAL_MODELS_DIR}/{champion_name}{suffix}.joblib"
                if os.path.exists(candidate):
                    champion_src = candidate
                    break

    if champion_src and os.path.exists(champion_src):
        dst = f"{ARTIFACTS_DIR}/champion_model.joblib"
        shutil.copy2(champion_src, dst)
        print(f"Champion model: {champion_name}")
        print(f"Saved to: {dst}")
    else:
        # Use best_tuned_model.joblib if available
        best_path = f"{TUNED_DIR}/best_tuned_model.joblib"
        if os.path.exists(best_path):
            shutil.copy2(best_path, f"{ARTIFACTS_DIR}/champion_model.joblib")
            champion_name = "best_tuned_model"
            print(f"Champion model: {champion_name}")

    champion_info = {
        "champion_model": champion_name,
        "model_file": f"{ARTIFACTS_DIR}/champion_model.joblib",
    }
    with open(f"{ARTIFACTS_DIR}/champion_model_info.json", "w") as f:
        json.dump(champion_info, f, indent=2)


def generate_artifacts_manifest():
    import json
    import glob
    import hashlib

    def md5_of_file(path):
        h = hashlib.md5()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()

    manifest = {
        "pipeline": "Student Performance ML Pipeline",
        "generated_at": datetime.utcnow().isoformat(),
        "artifacts": {},
    }

    # Catalogue all important artifacts
    categories = {
        "preprocessing": f"{ARTIFACTS_DIR}/preprocessing",
        "models": MODELS_DIR,
        "tuned_models": TUNED_DIR,
        "final_models": FINAL_MODELS_DIR,
        "metrics": f"{ARTIFACTS_DIR}/metrics",
        "root": ARTIFACTS_DIR,
    }

    for category, directory in categories.items():
        if not os.path.exists(directory):
            continue
        files = []
        # Only joblib and json files
        for ext in ["*.joblib", "*.json"]:
            for fpath in glob.glob(f"{directory}/{ext}"):
                if os.path.isfile(fpath):
                    files.append({
                        "file": os.path.basename(fpath),
                        "path": fpath,
                        "size_bytes": os.path.getsize(fpath),
                        "md5": md5_of_file(fpath),
                    })
        if files:
            manifest["artifacts"][category] = files

    with open(f"{ARTIFACTS_DIR}/manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    total = sum(len(v) for v in manifest["artifacts"].values())
    print(f"\nManifest generated: {total} artifacts catalogued")
    print(f"Saved to: {ARTIFACTS_DIR}/manifest.json")

    print("\n=== PIPELINE COMPLETE ===")
    print("All models have been extracted and catalogued.")
    print(f"Artifacts directory: {ARTIFACTS_DIR}")
    print(f"Champion model: {ARTIFACTS_DIR}/champion_model.joblib")


with DAG(
    dag_id="06_model_extractor",
    default_args=DEFAULT_ARGS,
    description="Extract final models as joblib files and generate artifact manifest",
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["model-extraction", "artifacts"],
) as dag:

    task_extract = PythonOperator(
        task_id="extract_all_models",
        python_callable=extract_all_models,
    )

    task_champion = PythonOperator(
        task_id="identify_champion_model",
        python_callable=identify_champion_model,
    )

    task_manifest = PythonOperator(
        task_id="generate_artifacts_manifest",
        python_callable=generate_artifacts_manifest,
    )

    task_extract >> task_champion >> task_manifest
