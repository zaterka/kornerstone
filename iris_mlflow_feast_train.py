from hera.workflows import Steps, Workflow, WorkflowsService, script
import os
import requests
import time


# Task to train the model and log to MLflow
@script(image="python:3.12")
def train_model():
    import subprocess

    # Install required packages
    subprocess.run(
        ["pip", "install", "scikit-learn", "pandas", "mlflow", "feast"],
        check=True,
        stdout=subprocess.PIPE,
        universal_newlines=True,
    )

    import pandas as pd
    import mlflow
    from sklearn import datasets
    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    from datetime import datetime
    from feast import FeatureStore
    
    # Configure MLflow
    mlflow_uri = "http://mlflow-server.kornerstone-ml.svc.cluster.local:5000"
    
    # Test connection with retry
    max_retries = 5
    for i in range(max_retries):
        try:
            response = requests.get(f"{mlflow_uri}/health")
            if response.status_code == 200:
                print("Successfully connected to MLflow server")
                break
        except requests.exceptions.RequestException as e:
            print(f"Attempt {i+1}/{max_retries}: Failed to connect to MLflow server: {e}")
            if i < max_retries - 1:
                time.sleep(5)
            else:
                raise Exception("Failed to connect to MLflow server after multiple attempts")

    mlflow.set_tracking_uri(mlflow_uri)
    mlflow.set_experiment("iris-classification")

    # Load Iris dataset
    iris = datasets.load_iris()
    
    # Create a DataFrame for Feast
    feature_df = pd.DataFrame(
        iris.data, 
        columns=['sepal_length', 'sepal_width', 'petal_length', 'petal_width']
    )
    feature_df['target'] = iris.target
    feature_df['timestamp'] = pd.Timestamp.now()
    feature_df['id'] = range(len(feature_df))

    # Initialize Feast Feature Store
    store = FeatureStore(repo_path="./feature_repo")
    
    # Save features to Feast
    store.get_or_create_entity("iris_id", description="Iris sample ID")
    store.get_or_create_feature_view(
        name="iris_features",
        entities=["iris_id"],
        features=[
            "sepal_length",
            "sepal_width",
            "petal_length",
            "petal_width",
            "target"
        ],
        online=True,
        input=feature_df
    )
    
    # Prepare data for training
    X = iris.data
    y = iris.target

    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Start MLflow run
    with mlflow.start_run():
        # Train a Logistic Regression model
        model = LogisticRegression(max_iter=200)
        model.fit(X_train, y_train)

        # Make predictions
        y_pred = model.predict(X_test)

        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted')
        recall = recall_score(y_test, y_pred, average='weighted')
        f1 = f1_score(y_test, y_pred, average='weighted')

        # Log parameters
        mlflow.log_param("model_type", "LogisticRegression")
        mlflow.log_param("train_size", len(X_train))
        mlflow.log_param("test_size", len(X_test))

        # Log metrics
        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("precision", precision)
        mlflow.log_metric("recall", recall)
        mlflow.log_metric("f1", f1)

        # Log model
        mlflow.sklearn.log_model(model, "model")

        print(f"Accuracy: {accuracy * 100:.2f}%")
        print(f"Precision: {precision * 100:.2f}%")
        print(f"Recall: {recall * 100:.2f}%")
        print(f"F1 Score: {f1 * 100:.2f}%")


with Workflow(
    generate_name="iris-classifier-",
    entrypoint="steps",
    namespace="kornerstone-ml",
    workflows_service=WorkflowsService(host="https://localhost:2746", verify_ssl=False),
) as w:
    with Steps(name="steps") as train:
        train_model()

w.create() 