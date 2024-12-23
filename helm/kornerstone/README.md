# Kornerstone Helm Chart

A Helm chart for deploying the Kornerstone ML Platform - a complete ML platform that includes MLflow, Feast, Argo Workflows, and KServe.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- PV provisioner support in the underlying infrastructure

## Installing the Chart

1. Add the required Helm repositories:

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update
```

2. Install the chart:

```bash
helm install kornerstone ./kornerstone
```

## Configuration

The following table lists the configurable parameters of the Kornerstone chart and their default values.

### Global Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `global.namespace` | Namespace to deploy into | `kornerstone-ml` |
| `global.storageClass` | Storage class for PVCs | `manual` |

### PostgreSQL Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `postgresql.enabled` | Enable PostgreSQL deployment | `true` |
| `postgresql.auth.username` | PostgreSQL username | `feast` |
| `postgresql.auth.password` | PostgreSQL password | `feast123` |

### MLflow Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `mlflow.enabled` | Enable MLflow deployment | `true` |
| `mlflow.image.repository` | MLflow image repository | `mlflow-custom` |
| `mlflow.service.type` | MLflow service type | `ClusterIP` |

### MinIO Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `minio.enabled` | Enable MinIO deployment | `true` |
| `minio.auth.rootUser` | MinIO root user | `minio` |
| `minio.auth.rootPassword` | MinIO root password | `minio123` |

### Feast Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `feast.enabled` | Enable Feast deployment | `true` |
| `feast.image.repository` | Feast image repository | `feastdev/feature-server` |
| `feast.service.type` | Feast service type | `LoadBalancer` |

### Argo Workflows Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `argo.enabled` | Enable Argo Workflows deployment | `true` |
| `argo.server.service.type` | Argo server service type | `LoadBalancer` |

### KServe Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `kserve.enabled` | Enable KServe deployment | `true` |

## Usage

After installing the chart, you can access the following services:

- MLflow UI: Access through the MLflow service
- Feast: Access through the Feast service
- Argo Workflows UI: Access through the Argo server service
- MinIO Console: Access through the MinIO console service

## Uninstalling the Chart

To uninstall/delete the `kornerstone` deployment:

```bash
helm uninstall kornerstone
``` 