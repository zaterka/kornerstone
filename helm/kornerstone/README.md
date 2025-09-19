# Kornerstone Helm Chart

A comprehensive Helm chart for deploying the Kornerstone ML Platform - a complete, production-ready machine learning platform that includes all essential components for the ML lifecycle.

## 🏗️ Chart Architecture

This chart deploys the following components:

### Core ML Components
- **MLflow** - Experiment tracking and model registry (custom deployment)
- **Feast** - Feature store and management (custom deployment)
- **KServe** - Model serving platform (custom deployment)

### Infrastructure Components (Sub-charts)
- **MinIO** - S3-compatible object storage (Bitnami chart)
- **PostgreSQL** - Database for metadata and features (Bitnami chart)
- **Argo Workflows** - ML pipeline orchestration (Argo chart)

### Optional Components
- **Prometheus Stack** - Monitoring and observability (Prometheus Community chart)

## 📋 Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- PV provisioner support in the underlying infrastructure
- Storage class configured (default: `standard`)

## 🚀 Installation

### 1. Add Required Helm Repositories

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add argo https://argoproj.github.io/argo-helm
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```

### 2. Install the Chart

```bash
# Basic installation
helm install kornerstone ./kornerstone --namespace kornerstone-ml --create-namespace

# With custom values
helm install kornerstone ./kornerstone -f custom-values.yaml --namespace kornerstone-ml --create-namespace

# Using the deployment script
../../../deploy.sh
```

## ⚙️ Configuration

### Global Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `global.namespace` | Namespace to deploy into | `kornerstone-ml` |
| `global.storageClass` | Storage class for PVCs | `standard` |
| `global.image.pullPolicy` | Image pull policy | `IfNotPresent` |

### Component Enable/Disable

| Parameter | Description | Default |
|-----------|-------------|---------|
| `mlflow.enabled` | Enable MLflow deployment | `true` |
| `feast.enabled` | Enable Feast deployment | `true` |
| `argo.enabled` | Enable Argo Workflows deployment | `true` |
| `kserve.enabled` | Enable KServe deployment | `true` |
| `minio.enabled` | Enable MinIO deployment | `true` |
| `postgresql.enabled` | Enable PostgreSQL deployment | `true` |
| `monitoring.enabled` | Enable monitoring stack | `false` |

### MLflow Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `mlflow.service.type` | MLflow service type | `ClusterIP` |
| `mlflow.service.port` | MLflow service port | `5000` |

### Feast Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `feast.image.repository` | Feast image repository | `feastdev/feature-server` |
| `feast.image.tag` | Feast image tag | `0.34.1` |
| `feast.service.type` | Feast service type | `ClusterIP` |
| `feast.service.port` | Feast service port | `6566` |
| `feast.config.project` | Feast project name | `kornerstone` |

### MinIO Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `minio.auth.rootUser` | MinIO root user | `minio` |
| `minio.auth.rootPassword` | MinIO root password | `minio123` |
| `minio.persistence.size` | MinIO storage size | `10Gi` |
| `minio.service.ports.api` | MinIO API port | `9000` |
| `minio.service.ports.console` | MinIO console port | `9001` |

### PostgreSQL Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `postgresql.auth.username` | PostgreSQL username | `feast` |
| `postgresql.auth.password` | PostgreSQL password | `feast123` |
| `postgresql.auth.database` | Primary database | `feast` |
| `postgresql.auth.databases` | Additional databases | `["mlflow", "feast"]` |
| `postgresql.primary.persistence.size` | PostgreSQL storage size | `10Gi` |

### Argo Workflows Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `argo.server.service.type` | Argo server service type | `ClusterIP` |
| `argo.workflow.serviceAccount.create` | Create service account | `true` |
| `argo.workflow.serviceAccount.name` | Service account name | `argo-workflow` |

### KServe Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `kserve.serviceAccount.create` | Create service account | `true` |
| `kserve.serviceAccount.name` | Service account name | `kserve-sa` |

## 🔧 Advanced Configuration

### Custom Storage Classes

```yaml
global:
  storageClass: fast-ssd

minio:
  persistence:
    storageClass: fast-ssd

postgresql:
  primary:
    persistence:
      storageClass: fast-ssd
```

### Resource Limits

```yaml
mlflow:
  resources:
    limits:
      cpu: 2000m
      memory: 4Gi
    requests:
      cpu: 500m
      memory: 1Gi

feast:
  resources:
    limits:
      cpu: 1000m
      memory: 2Gi
    requests:
      cpu: 200m
      memory: 512Mi
```

### External Services

```yaml
postgresql:
  enabled: false
  external:
    host: external-postgres.example.com
    port: 5432
    username: feast
    password: secure-password
    database: feast

minio:
  enabled: false
  external:
    endpoint: s3.amazonaws.com
    accessKey: AKIA...
    secretKey: SECRET...
    bucket: my-ml-bucket
```

## 🔍 Chart Structure

```
kornerstone/
├── Chart.yaml                          # Chart metadata and dependencies
├── values.yaml                         # Default configuration values
├── templates/
│   ├── _helpers.tpl                    # Template helpers
│   ├── NOTES.txt                       # Post-installation notes
│   │
│   ├── mlflow-deployment.yaml          # MLflow deployment
│   ├── mlflow-service.yaml             # MLflow service
│   │
│   ├── feast-deployment.yaml           # Feast deployment
│   ├── feast-service.yaml              # Feast service
│   ├── feast-configmap.yaml            # Feast configuration
│   │
│   ├── kserve-deployment.yaml          # KServe inference service
│   ├── kserve-service-account.yaml     # KServe RBAC
│   ├── kserve-configmap.yaml           # KServe configuration
│   │
│   ├── minio-init-job.yaml             # MinIO initialization
│   ├── minio-bucket-job.yaml           # MinIO bucket creation
│   ├── minio-service-account.yaml      # MinIO service account
│   │
│   ├── argo-workflow-configmap.yaml    # Argo configuration
│   ├── pre-argo-hook.yaml              # Argo pre-installation hooks
│   │
│   ├── cleanup-job.yaml                # Pre-installation cleanup
│   ├── deployment-hooks.yaml           # Various deployment hooks
│   ├── connectivity-test.yaml          # Connectivity testing
│   └── test-script-configmap.yaml      # Test scripts
│
└── charts/                             # Sub-chart dependencies (auto-generated)
    ├── minio/
    ├── postgresql/
    ├── argo-workflows/
    └── kube-prometheus-stack/
```

## 🧪 Testing

### Helm Chart Testing

```bash
# Lint the chart
helm lint ./kornerstone

# Template rendering test
helm template kornerstone ./kornerstone --debug

# Dry run installation
helm install kornerstone ./kornerstone --dry-run --debug

# Run Helm tests
helm test kornerstone -n kornerstone-ml
```

### Integration Testing

```bash
# Apply connectivity tests
kubectl apply -f templates/connectivity-test.yaml

# Check all pods are running
kubectl get pods -n kornerstone-ml

# Verify services are accessible
kubectl get svc -n kornerstone-ml
```

## 🔧 Troubleshooting

### Common Issues

1. **Dependency Download Failures**
   ```bash
   helm dependency update ./kornerstone
   ```

2. **Storage Class Issues**
   ```bash
   kubectl get storageclass
   # Update values.yaml with correct storage class
   ```

3. **Resource Conflicts**
   ```bash
   helm uninstall kornerstone -n kornerstone-ml
   kubectl delete namespace kornerstone-ml
   ```

4. **KServe Certificate Issues**
   ```bash
   # Install cert-manager first
   kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.11.0/cert-manager.yaml
   ```

### Debug Commands

```bash
# Check Helm release status
helm status kornerstone -n kornerstone-ml

# View Helm release history
helm history kornerstone -n kornerstone-ml

# Get detailed information about a specific resource
kubectl describe pod <pod-name> -n kornerstone-ml

# View logs
kubectl logs -f deployment/kornerstone-mlflow -n kornerstone-ml
```

## 🔄 Upgrading

```bash
# Upgrade to new version
helm upgrade kornerstone ./kornerstone -n kornerstone-ml

# Upgrade with new values
helm upgrade kornerstone ./kornerstone -f new-values.yaml -n kornerstone-ml

# Force upgrade (use with caution)
helm upgrade kornerstone ./kornerstone --force -n kornerstone-ml
```

## 🗑️ Uninstalling

```bash
# Uninstall the release
helm uninstall kornerstone -n kornerstone-ml

# Clean up namespace (optional)
kubectl delete namespace kornerstone-ml

# Clean up persistent volumes (if needed)
kubectl delete pv -l app.kubernetes.io/instance=kornerstone
```

## 🤝 Contributing

To contribute to the chart:

1. Make changes to templates or values
2. Test locally with `helm template`
3. Run lint checks with `helm lint`
4. Test installation in a dev cluster
5. Update this README if needed
6. Submit a pull request

## 📄 License

This chart is licensed under the MIT License - see the [LICENSE](../../../LICENSE) file for details. 