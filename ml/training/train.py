import os
import mlflow
from sklearn.datasets import load_diabetes
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

def main():
    # MLflow setup
    mlflow.set_tracking_uri(os.environ.get('MLFLOW_TRACKING_URI'))
    mlflow.set_experiment(os.environ.get('MLFLOW_EXPERIMENT_NAME', 'default'))

    # Load sample dataset
    diabetes = load_diabetes()
    X, y = diabetes.data, diabetes.target

    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Train model
    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)

    # Evaluate
    y_pred = rf.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    # Log metrics and model
    with mlflow.start_run():
        mlflow.log_metric("mse", mse)
        mlflow.log_metric("r2", r2)
        
        # Log model
        mlflow.sklearn.log_model(
            rf, 
            "model",
            registered_model_name=os.environ.get('MODEL_NAME', 'diabetes-model')
        )

if __name__ == "__main__":
    main() 