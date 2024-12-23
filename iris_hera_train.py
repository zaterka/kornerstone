from hera.workflows import Steps, Workflow, WorkflowsService, script


# Task to train the model
@script(image="python:3.12")
def train_model():
    import subprocess

    subprocess.run(
        ["pip", "install", "scikit-learn", "pandas"],
        check=True,
        stdout=subprocess.PIPE,
        universal_newlines=True,
    )

    import pandas as pd
    from sklearn import datasets
    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score

    # Load Iris dataset
    iris = datasets.load_iris()
    X = iris.data
    y = iris.target

    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Train a Logistic Regression model
    model = LogisticRegression(max_iter=200)
    model.fit(X_train, y_train)

    # Predict and evaluate the model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {accuracy * 100:.2f}%")


with Workflow(
    generate_name="iris-classifier-",
    entrypoint="steps",
    namespace="kornerstone-ml",
    workflows_service=WorkflowsService(host="https://localhost:2746", verify_ssl=False),
) as w:
    with Steps(name="steps") as train:
        train_model()

w.create()
