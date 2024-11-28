# Kubernetes Native ML Platform

This repository contains the implementation of a Kubernetes-native machine learning platform using:
- Argo Workflows for ML pipeline orchestration
- MinIO for object storage
- MLflow for experiment tracking and model registry
- KServe for model serving

## Prerequisites
- Kubernetes cluster
- kubectl
- kustomize (included in recent kubectl versions)

## Quick Start
To deploy all components:

```bash
kubectl apply -