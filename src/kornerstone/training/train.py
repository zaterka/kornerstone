"""Training module for ML models."""

import os
import mlflow
from feast import FeatureStore
from sklearn.ensemble import RandomForestRegressor


def train_model(feature_store: FeatureStore, experiment_name: str):
    """Train a model using features from Feast."""
    mlflow.set_experiment(experiment_name)
    # Training logic here
    pass
