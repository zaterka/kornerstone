#!/bin/bash
set -e

NAMESPACE="kornerstone-ml"
RELEASE_NAME="kornerstone"
CHART_DIR="./helm/kornerstone"
REBUILD_DEPS=false
CLEAN_KSERVE=false

# Print with colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --rebuild-deps)
      REBUILD_DEPS=true
      shift
      ;;
    --namespace)
      NAMESPACE="$2"
      shift 2
      ;;
    --release-name)
      RELEASE_NAME="$2"
      shift 2
      ;;
    --clean-kserve)
      CLEAN_KSERVE=true
      shift
      ;;
    *)
      echo -e "${RED}Unknown argument: $1${NC}"
      exit 1
      ;;
  esac
done

echo -e "${BLUE}Kornerstone ML Platform Deployment${NC}"
echo -e "${BLUE}===============================${NC}"
echo -e "Namespace: ${GREEN}${NAMESPACE}${NC}"
echo -e "Release name: ${GREEN}${RELEASE_NAME}${NC}"

# Check if helm is installed
if ! command -v helm &> /dev/null; then
    echo -e "${RED}Error: helm is not installed. Please install helm first.${NC}"
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl is not installed. Please install kubectl first.${NC}"
    exit 1
fi

# Add required Helm repositories
echo -e "${GREEN}Adding Helm repositories...${NC}"
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add argo https://argoproj.github.io/argo-helm
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Clean up existing KServe resources if requested
if [[ "$CLEAN_KSERVE" == "true" ]]; then
    echo -e "${YELLOW}Cleaning up existing KServe resources...${NC}"
    
    # Check if the namespace exists before trying to delete resources
    if kubectl get namespace $NAMESPACE &> /dev/null; then
        # Delete any existing KServe InferenceService resources
        if kubectl get crd inferenceservices.serving.kserve.io &> /dev/null; then
            echo -e "${YELLOW}Deleting KServe InferenceServices in namespace ${NAMESPACE}...${NC}"
            kubectl delete inferenceservices --all -n $NAMESPACE --ignore-not-found=true || true
            
            # Wait to ensure resources are removed
            echo -e "${YELLOW}Waiting for KServe resources to be removed...${NC}"
            sleep 5
        fi
    fi
fi

# Update dependencies
echo -e "${GREEN}Updating Helm dependencies...${NC}"
if [[ "$REBUILD_DEPS" == "true" ]]; then
    echo -e "${YELLOW}Rebuilding dependencies (deleting charts directory)...${NC}"
    rm -rf ${CHART_DIR}/charts
fi
helm dependency update $CHART_DIR || {
    echo -e "${RED}Failed to update dependencies. Try running with --rebuild-deps flag.${NC}"
    exit 1
}

# Check if namespace exists, create if it doesn't
if ! kubectl get namespace $NAMESPACE &> /dev/null; then
    echo -e "${GREEN}Creating namespace $NAMESPACE...${NC}"
    kubectl create namespace $NAMESPACE
fi

# Check if KServe is installed
if ! kubectl get crd inferenceservices.serving.kserve.io &> /dev/null; then
    echo -e "${RED}WARNING: KServe CRDs not found.${NC}"
    echo -e "${GREEN}Would you like to install KServe CRDs? (y/n)${NC}"
    read -r install_kserve
    
    if [[ "$install_kserve" == "y" ]]; then
        # Check if cert-manager is installed
        if ! kubectl get crd certificates.cert-manager.io &> /dev/null; then
            echo -e "${YELLOW}WARNING: cert-manager is not installed. Some KServe features may not work properly.${NC}"
            echo -e "${YELLOW}You can install cert-manager later with: kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.11.0/cert-manager.yaml${NC}"
            echo -e "${GREEN}Continuing with KServe installation (some errors about Certificate and Issuer resources are expected)...${NC}"
        fi
        
        echo -e "${GREEN}Installing KServe CRDs...${NC}"
        # Using direct URL to KServe CRDs
        kubectl apply -f https://github.com/kserve/kserve/releases/download/v0.11.0/kserve.yaml || true
        kubectl apply -f https://github.com/kserve/kserve/releases/download/v0.11.0/kserve-runtimes.yaml || true
        
        echo -e "${GREEN}Waiting for KServe CRDs to be ready...${NC}"
        kubectl wait --for=condition=established --timeout=60s crd/inferenceservices.serving.kserve.io || true
        
        echo -e "${GREEN}KServe installation completed. Some certificate-related errors are expected and can be ignored.${NC}"
    fi
fi

# Deploy Kornerstone
echo -e "${GREEN}Deploying Kornerstone ML Platform...${NC}"

# Run the Helm install/upgrade command with appropriate flags
if [[ "$CLEAN_KSERVE" == "true" ]]; then
    # When doing a clean install after KServe cleanup, use --force flag
    helm upgrade --install $RELEASE_NAME $CHART_DIR --namespace $NAMESPACE \
      --set global.namespace=$NAMESPACE \
      --force \
      --debug
else
    # Normal install/upgrade
    helm upgrade --install $RELEASE_NAME $CHART_DIR --namespace $NAMESPACE \
      --set global.namespace=$NAMESPACE \
      --debug
fi

echo -e "${GREEN}Deployment initiated!${NC}"
echo -e "${GREEN}Checking deployment status...${NC}"

# Wait for pods to be ready
sleep 5
kubectl get pods -n $NAMESPACE

echo -e "${BLUE}Usage Instructions${NC}"
echo -e "${BLUE}==================${NC}"
echo -e "${GREEN}To access the services, run the following commands in separate terminals:${NC}"
echo -e "${GREEN}MLflow UI:${NC}"
echo -e "kubectl port-forward svc/$RELEASE_NAME-mlflow 5000:5000 -n $NAMESPACE"
echo -e "${GREEN}MinIO Console:${NC}"
echo -e "kubectl port-forward svc/$RELEASE_NAME-minio 9001:9001 -n $NAMESPACE"
echo -e "${GREEN}Feast Feature Server:${NC}"
echo -e "kubectl port-forward svc/$RELEASE_NAME-feast 6566:6566 -n $NAMESPACE"
echo -e "${GREEN}Argo Workflows UI:${NC}"
echo -e "kubectl port-forward svc/$RELEASE_NAME-argo-workflows-server 2746:2746 -n $NAMESPACE"

echo -e "\n${GREEN}If you encounter issues with KServe, try running:${NC}"
echo -e "./deploy.sh --clean-kserve\n"

echo -e "${GREEN}Thank you for using Kornerstone ML Platform!${NC}" 