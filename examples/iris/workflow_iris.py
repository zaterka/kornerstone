#!/usr/bin/env python3
"""
Argo Workflows (Hera) pipeline: Train Iris RF and deploy via KServe

Steps:
1) Train model with examples/iris/train_iris.py → uploads to MinIO and writes model URI
2) Apply KServe InferenceService manifest (points to s3://mlflow/models/iris-rf)

Prereqs:
- Cluster has Kornerstone chart installed in namespace kornerstone-ml
- Argo Workflows is running (part of chart)
- ServiceAccount argo-workflow has access (chart config)

Usage:
  python examples/iris/workflow_iris.py --namespace kornerstone-ml --submit
"""
from __future__ import annotations

import argparse
from hera.workflows import DAG, Env, Parameter, Resources, Script, Workflow


def build_workflow(namespace: str) -> Workflow:
    wf = Workflow(
        generate_name="iris-rf-",
        namespace=namespace,
        service_account_name="argo-workflow",
    )

    model_uri_param = Parameter(name="model_uri", value="s3://mlflow/models/iris-rf")

    # Load local files to inline into steps
    train_src_path = "/Users/pedro.zaterka/personal-projects/kornerstone/examples/iris/train_iris.py"
    isvc_path = "/Users/pedro.zaterka/personal-projects/kornerstone/examples/iris/kserve_inferenceservice.yaml"
    with open(train_src_path, "r", encoding="utf-8") as f:
        train_src = f.read()
    with open(isvc_path, "r", encoding="utf-8") as f:
        isvc_yaml = f.read()

    with wf:
        with DAG(name="main"):
            train = Script(
                name="train",
                image="python:3.12-slim",
                command=["bash", "-lc"],
                source=(
                    "apt-get update && apt-get install -y --no-install-recommends ca-certificates && "
                    "pip install --no-cache-dir scikit-learn==1.5.1 mlflow==2.10.0 boto3==1.34.162 joblib==1.4.2 && "
                    "mkdir -p /app && cat > /app/train_iris.py << 'PY'\n" + train_src + "\nPY\n" \
                    + "python /app/train_iris.py\n"
                ),
                env=[
                    Env(name="MLFLOW_TRACKING_URI", value=f"http://kornerstone-mlflow:5000"),
                    Env(name="MLFLOW_S3_ENDPOINT_URL", value=f"http://kornerstone-minio:9000"),
                    # These require Argo to project the secret as env vars. Hera supports value_from with dicts.
                    Env(name="AWS_ACCESS_KEY_ID", value_from={"secret_key_ref": {"name": "kornerstone-minio", "key": "root-user"}}),
                    Env(name="AWS_SECRET_ACCESS_KEY", value_from={"secret_key_ref": {"name": "kornerstone-minio", "key": "root-password"}}),
                    Env(name="MODEL_URI_PATH", value="/tmp/model_uri.txt"),
                ],
                resources=Resources(cpu_request="200m", memory_request="512Mi"),
            )

            deploy = Script(
                name="deploy",
                image="bitnami/kubectl:latest",
                command=["bash", "-lc"],
                source=(
                    "cat >/tmp/isvc.yaml << 'YAML'\n" + isvc_yaml + "\nYAML\n" \
                    + "kubectl apply -n " + namespace + " -f /tmp/isvc.yaml\n"
                ),
            )

            train >> deploy

    return wf


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--namespace", default="kornerstone-ml")
    parser.add_argument("--submit", action="store_true")
    args = parser.parse_args()
    wf = build_workflow(args.namespace)
    if args.submit:
        wf.create()
    else:
        print(wf.to_yaml())


if __name__ == "__main__":
    main()


