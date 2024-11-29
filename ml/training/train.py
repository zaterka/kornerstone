import os
import mlflow
from feast import FeatureStore
from sklearn.datasets import load_diabetes
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

def get_feature_store():
    return FeatureStore(repo_path="/etc/feast")

def get_training_data(feature_store):
    # This is an example - replace with your actual feature retrieval logic
    entity_df = feature_store.get_historical_features(
        entity_df=your_entity_df,
        features=[
            "feature_view:feature1",
            "feature_view:feature2",
            # ... other features
        ],
    ).to_df()
    return entity_df

def main():
    # MLflow setup
    mlflow.set_tracking_uri(os.environ.get('MLFLOW_TRACKING_URI'))
    mlflow.set_experiment(os.environ.get('MLFLOW_EXPERIMENT_NAME', 'default'))

    # Initialize feature store
    store = get_feature_store()
    
    # Get training data from Feast
    training_data = get_training_data(store)
    
    # Split dataset
    X = training_data.drop('target', axis=1)  # Adjust column names as needed
    y = training_data['target']
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Rest of your training code remains the same
    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)

    y_pred = rf.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    with mlflow.start_run():
        mlflow.log_metric("mse", mse)
        mlflow.log_metric("r2", r2)
        mlflow.sklearn.log_model(
            rf, 
            "model",
            registered_model_name=os.environ.get('MODEL_NAME', 'diabetes-model')
        )

if __name__ == "__main__":
    main() 