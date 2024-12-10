"""Model serving module."""
from feast import FeatureStore
import mlflow

def load_model(model_name: str, stage: str = "Production"):
    """Load a model from MLflow."""
    return mlflow.pyfunc.load_model(f"models:/{model_name}/{stage}") 