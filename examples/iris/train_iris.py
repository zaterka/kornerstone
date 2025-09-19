#!/usr/bin/env python3
"""
Iris RandomForest training script

Actions:
- Loads the iris dataset and trains a RandomForestClassifier
- Logs metrics and model to MLflow (tracking URI via MLFLOW_TRACKING_URI)
- Saves a joblib model and uploads it to MinIO S3 bucket "mlflow" at models/iris-rf/model.joblib
- Writes the model storage URI to /tmp/model_uri.txt for pipeline handoff

Environment required inside cluster (defaults target the Helm release namespace):
- MLFLOW_TRACKING_URI (default: http://kornerstone-mlflow:5000)
- MLFLOW_S3_ENDPOINT_URL (default: http://kornerstone-minio:9000)
- AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY from secret kornerstone-minio
"""
from __future__ import annotations

import os
import time
from typing import Tuple

import boto3
import joblib
import mlflow
import numpy as np
import pandas as pd
from botocore.client import Config
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split


def get_env(name: str, default: str) -> str:
    value = os.getenv(name, default)
    return value


def train_model(random_state: int = 42) -> Tuple[RandomForestClassifier, float]:
    iris = load_iris(as_frame=True)
    X: pd.DataFrame = iris.data
    y: pd.Series = iris.target
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=random_state, stratify=y
    )
    model = RandomForestClassifier(n_estimators=200, random_state=random_state)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    acc = float(accuracy_score(y_test, preds))
    return model, acc


def upload_to_minio(local_path: str, bucket: str, key: str) -> str:
    endpoint = get_env("MLFLOW_S3_ENDPOINT_URL", "http://kornerstone-minio:9000")
    access_key = os.environ["AWS_ACCESS_KEY_ID"]
    secret_key = os.environ["AWS_SECRET_ACCESS_KEY"]
    s3 = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )
    try:
        s3.head_bucket(Bucket=bucket)
    except Exception:
        s3.create_bucket(Bucket=bucket)
    s3.upload_file(local_path, bucket, key)
    return f"s3://{bucket}/{key.rsplit('/', 1)[0]}"


def main() -> None:
    tracking_uri = get_env("MLFLOW_TRACKING_URI", "http://kornerstone-mlflow:5000")
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment("iris-rf")

    with mlflow.start_run(run_name=f"iris-rf-{int(time.time())}"):
        model, acc = train_model()
        mlflow.log_metric("accuracy", acc)
        mlflow.sklearn.log_model(model, artifact_path="model")

        os.makedirs("/tmp", exist_ok=True)
        local_model_path = "/tmp/model.joblib"
        joblib.dump(model, local_model_path)

        model_prefix = "models/iris-rf"
        model_uri = upload_to_minio(local_model_path, bucket="mlflow", key=f"{model_prefix}/model.joblib")

        out_path = get_env("MODEL_URI_PATH", "/tmp/model_uri.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(model_uri)

        print(f"Trained model accuracy={acc:.4f}")
        print(f"Model uploaded to: {model_uri}")
        print(f"Model URI written to: {out_path}")


if __name__ == "__main__":
    main()


