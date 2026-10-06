# Student Performance MLOps Pipeline

## Overview

An end-to-end MLOps project for predicting student exam performance using machine learning.

The project implements a complete machine learning pipeline covering data preprocessing, model selection, model training, hyperparameter tuning, evaluation, model storage, API deployment, and a web-based frontend.

## Architecture

The pipeline uses:

- Apache Airflow for workflow orchestration
- MySQL for data storage
- Scikit-learn for machine learning
- Joblib for model serialization
- FastAPI for model serving
- React and Vite for the frontend
- Docker and Docker Compose for containerisation

## Machine Learning Pipeline

The pipeline processes the Student Performance Factors dataset.

The target variable is `Exam_Score`.

The Airflow pipeline includes:

1. Data preprocessing and loading into MySQL
2. Comparison of multiple regression models
3. Model training
4. Hyperparameter tuning
5. Model testing and evaluation
6. Extraction of the selected model for deployment

The models evaluated include:

- Linear Regression
- Ridge
- Lasso
- ElasticNet
- Decision Tree
- Random Forest
- Gradient Boosting
- Extra Trees

Random Forest and Gradient Boosting are also tuned using `RandomizedSearchCV`.

## API

The trained model is served through a FastAPI application.

The API provides prediction functionality through the `/predict` endpoint, allowing student information to be submitted and an exam-score prediction to be returned.

## Frontend

A React frontend provides:

- A prediction interface
- A model performance dashboard

The frontend communicates with the FastAPI backend.

## Running the Project

The project uses Docker Compose to run the different services.

```bash
docker compose up --build