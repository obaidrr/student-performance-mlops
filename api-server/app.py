"""
FastAPI server for Student Performance ML Pipeline.
Exposes endpoints for predictions, model info, and performance metrics.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import joblib
import json
import os
import numpy as np

app = FastAPI(
    title="Student Performance Prediction API",
    description="ML API for predicting student exam scores using trained models",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ARTIFACTS_DIR = os.getenv("ARTIFACTS_DIR", "/artifacts")
PREPROCESSING_DIR = f"{ARTIFACTS_DIR}/preprocessing"

_model = None
_scaler = None
_ordinal_encoders = None
_label_encoders = None
_metadata = None
_metrics = None

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


def load_artifacts():
    global _model, _scaler, _ordinal_encoders, _label_encoders, _metadata, _metrics

    champion_path = f"{ARTIFACTS_DIR}/champion_model.joblib"
    if os.path.exists(champion_path):
        _model = joblib.load(champion_path)
    else:
        # Try to find any available model
        import glob
        candidates = (
            glob.glob(f"{ARTIFACTS_DIR}/tuned_models/*_tuned.joblib") +
            glob.glob(f"{ARTIFACTS_DIR}/models/*_trained.joblib")
        )
        if candidates:
            _model = joblib.load(candidates[0])

    scaler_path = f"{PREPROCESSING_DIR}/numerical_scaler.joblib"
    if os.path.exists(scaler_path):
        _scaler = joblib.load(scaler_path)

    ordinal_path = f"{PREPROCESSING_DIR}/ordinal_encoders.joblib"
    if os.path.exists(ordinal_path):
        _ordinal_encoders = joblib.load(ordinal_path)

    label_path = f"{PREPROCESSING_DIR}/label_encoders.joblib"
    if os.path.exists(label_path):
        _label_encoders = joblib.load(label_path)

    metadata_path = f"{PREPROCESSING_DIR}/metadata.json"
    if os.path.exists(metadata_path):
        with open(metadata_path) as f:
            _metadata = json.load(f)

    metrics_path = f"{ARTIFACTS_DIR}/model_metrics.json"
    if os.path.exists(metrics_path):
        with open(metrics_path) as f:
            _metrics = json.load(f)


@app.on_event("startup")
async def startup_event():
    load_artifacts()


class PredictionInput(BaseModel):
    hours_studied: float = Field(..., ge=0, le=24, description="Hours studied per day")
    attendance: float = Field(..., ge=0, le=100, description="Attendance percentage")
    parental_involvement: str = Field(..., description="Low, Medium, or High")
    access_to_resources: str = Field(..., description="Low, Medium, or High")
    extracurricular_activities: str = Field(..., description="Yes or No")
    sleep_hours: float = Field(..., ge=0, le=24, description="Hours of sleep per day")
    previous_scores: float = Field(..., ge=0, le=100, description="Previous exam scores")
    motivation_level: str = Field(..., description="Low, Medium, or High")
    internet_access: str = Field(..., description="Yes or No")
    tutoring_sessions: int = Field(..., ge=0, description="Number of tutoring sessions")
    family_income: str = Field(..., description="Low, Medium, or High")
    teacher_quality: str = Field(..., description="Low, Medium, or High")
    school_type: str = Field(..., description="Public or Private")
    peer_influence: str = Field(..., description="Negative, Neutral, or Positive")
    physical_activity: int = Field(..., ge=0, description="Hours of physical activity per week")
    learning_disabilities: str = Field(..., description="Yes or No")
    parental_education_level: str = Field(..., description="High School, College, or Postgraduate")
    distance_from_home: str = Field(..., description="Near, Moderate, or Far")
    gender: str = Field(..., description="Male or Female")


class PredictionOutput(BaseModel):
    predicted_exam_score: float
    model_used: str
    confidence_note: str


class ModelInfo(BaseModel):
    name: str
    type: str
    status: str
    metrics: Optional[Dict[str, float]] = None


def preprocess_input(data: PredictionInput) -> np.ndarray:
    import pandas as pd

    raw = {
        "Hours_Studied": data.hours_studied,
        "Attendance": data.attendance,
        "Sleep_Hours": data.sleep_hours,
        "Previous_Scores": data.previous_scores,
        "Tutoring_Sessions": float(data.tutoring_sessions),
        "Physical_Activity": float(data.physical_activity),
        "Extracurricular_Activities": data.extracurricular_activities,
        "Internet_Access": data.internet_access,
        "Learning_Disabilities": data.learning_disabilities,
        "Gender": data.gender,
        "School_Type": data.school_type,
        "Parental_Involvement": data.parental_involvement,
        "Access_to_Resources": data.access_to_resources,
        "Motivation_Level": data.motivation_level,
        "Family_Income": data.family_income,
        "Teacher_Quality": data.teacher_quality,
        "Parental_Education_Level": data.parental_education_level,
        "Distance_from_Home": data.distance_from_home,
        "Peer_Influence": data.peer_influence,
    }

    df = pd.DataFrame([raw])

    if _scaler is not None:
        df[NUMERICAL_FEATURES] = _scaler.transform(df[NUMERICAL_FEATURES])

    if _ordinal_encoders is not None:
        for col, enc in _ordinal_encoders.items():
            df[col] = enc.transform(df[[col]])

    if _label_encoders is not None:
        for col, le in _label_encoders.items():
            val = df[col].iloc[0]
            if val in le.classes_:
                df[col] = le.transform(df[col].astype(str))
            else:
                df[col] = 0

    feature_cols = NUMERICAL_FEATURES + CATEGORICAL_BINARY + list(CATEGORICAL_ORDINAL.keys())
    return df[feature_cols].values


@app.get("/")
def root():
    return {
        "service": "Student Performance Prediction API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": ["/predict", "/models", "/model-performance", "/health"],
    }


@app.get("/health")
def health():
    model_loaded = _model is not None
    scaler_loaded = _scaler is not None
    return {
        "status": "healthy" if model_loaded else "degraded",
        "model_loaded": model_loaded,
        "scaler_loaded": scaler_loaded,
        "artifacts_dir": ARTIFACTS_DIR,
    }


@app.post("/predict", response_model=PredictionOutput)
def predict(input_data: PredictionInput):
    if _model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Run the ML pipeline first.",
        )

    try:
        features = preprocess_input(input_data)
        prediction = float(_model.predict(features)[0])
        prediction = max(0.0, min(100.0, prediction))

        model_name = type(_model).__name__
        return PredictionOutput(
            predicted_exam_score=round(prediction, 2),
            model_used=model_name,
            confidence_note="Prediction based on trained regression model",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@app.get("/models")
def list_models():
    import glob

    models = []
    for pattern, mtype in [
        (f"{ARTIFACTS_DIR}/models/*_trained.joblib", "trained"),
        (f"{ARTIFACTS_DIR}/tuned_models/*_tuned.joblib", "tuned"),
        (f"{ARTIFACTS_DIR}/final_models/*.joblib", "final"),
    ]:
        for path in glob.glob(pattern):
            name = os.path.basename(path).replace(".joblib", "")
            models.append({"name": name, "type": mtype, "path": path})

    champion_path = f"{ARTIFACTS_DIR}/champion_model.joblib"
    champion_info_path = f"{ARTIFACTS_DIR}/champion_model_info.json"
    champion_name = "unknown"
    if os.path.exists(champion_info_path):
        with open(champion_info_path) as f:
            info = json.load(f)
        champion_name = info.get("champion_model", "unknown")

    return {
        "models": models,
        "total": len(models),
        "champion": champion_name,
        "champion_model_available": os.path.exists(champion_path),
    }


@app.get("/model-performance")
def model_performance():
    if _metrics is None:
        metrics_path = f"{ARTIFACTS_DIR}/model_metrics.json"
        if not os.path.exists(metrics_path):
            raise HTTPException(
                status_code=404,
                detail="Metrics not found. Run the ML pipeline first.",
            )
        with open(metrics_path) as f:
            metrics = json.load(f)
    else:
        metrics = _metrics

    comparison_path = f"{ARTIFACTS_DIR}/model_comparison.json"
    comparison = None
    if os.path.exists(comparison_path):
        with open(comparison_path) as f:
            comparison = json.load(f)

    return {
        "champion_model": metrics.get("champion_model"),
        "champion_metrics": metrics.get("champion_metrics"),
        "all_models": metrics.get("all_models", {}),
        "model_comparison": comparison,
    }


@app.get("/model-performance/comparison")
def model_comparison():
    comparison_path = f"{ARTIFACTS_DIR}/model_comparison.json"
    if not os.path.exists(comparison_path):
        raise HTTPException(status_code=404, detail="Model comparison results not found")
    with open(comparison_path) as f:
        return json.load(f)


@app.post("/reload-model")
def reload_model():
    load_artifacts()
    return {"status": "reloaded", "model_loaded": _model is not None}
