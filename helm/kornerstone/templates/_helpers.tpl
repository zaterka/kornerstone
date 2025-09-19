{{/*
Common labels
*/}}
{{- define "kornerstone.labels" -}}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "kornerstone.selectorLabels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "kornerstone.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common init containers for waiting on PostgreSQL
*/}}
{{- define "kornerstone.postgresql.initContainer" -}}
- name: wait-for-postgresql
  image: postgres:15-alpine
  command: 
    - 'sh'
    - '-c'
    - |
      echo "Waiting for PostgreSQL to be ready..."
      until pg_isready -h {{ .Release.Name }}-postgresql -p 5432 -U {{ .Values.postgresql.auth.username }}; do
        echo "PostgreSQL is not ready yet, waiting 5 seconds..."
        sleep 5
      done
      echo "PostgreSQL is ready!"
      
      # Test database connection
      echo "Testing database connection..."
      PGPASSWORD="${POSTGRES_PASSWORD}" psql -h {{ .Release.Name }}-postgresql -p 5432 -U {{ .Values.postgresql.auth.username }} -d {{ .Values.postgresql.auth.database }} -c "SELECT 1;" || exit 1
      echo "Database connection successful!"
  env:
  - name: POSTGRES_PASSWORD
    valueFrom:
      secretKeyRef:
        name: {{ .Release.Name }}-postgresql
        key: password
{{- end }}

{{/*
Common init containers for waiting on MinIO
*/}}
{{- define "kornerstone.minio.initContainer" -}}
- name: wait-for-minio
  image: curlimages/curl:7.88.1
  command: 
    - 'sh'
    - '-c'
    - |
      echo "Waiting for MinIO to be ready..."
      until curl -f http://{{ .Release.Name }}-minio:{{ .Values.minio.service.ports.api }}/minio/health/live; do
        echo "MinIO is not ready yet, waiting 5 seconds..."
        sleep 5
      done
      echo "MinIO is ready!"
      
      # Test S3 API access
      echo "Testing MinIO S3 API access..."
      curl -f http://{{ .Release.Name }}-minio:{{ .Values.minio.service.ports.api }}/minio/health/ready || exit 1
      echo "MinIO S3 API is accessible!"
{{- end }}

{{/*
Common init containers for waiting on MLflow
*/}}
{{- define "kornerstone.mlflow.initContainer" -}}
- name: wait-for-mlflow
  image: curlimages/curl:7.88.1
  command: 
    - 'sh'
    - '-c'
    - |
      echo "Waiting for MLflow to be ready..."
      until curl -f http://{{ .Release.Name }}-mlflow:{{ .Values.mlflow.service.port }}/health; do
        echo "MLflow is not ready yet, waiting 10 seconds..."
        sleep 10
      done
      echo "MLflow is ready!"
      
      # Test MLflow API
      echo "Testing MLflow API..."
      curl -f http://{{ .Release.Name }}-mlflow:{{ .Values.mlflow.service.port }}/api/2.0/mlflow/experiments/list || exit 1
      echo "MLflow API is accessible!"
{{- end }}

{{/*
Common init containers for waiting on Feast
*/}}
{{- define "kornerstone.feast.initContainer" -}}
- name: wait-for-feast
  image: curlimages/curl:7.88.1
  command: 
    - 'sh'
    - '-c'
    - |
      echo "Waiting for Feast to be ready..."
      until curl -f http://{{ .Release.Name }}-feast:{{ .Values.feast.service.port }}/health; do
        echo "Feast is not ready yet, waiting 10 seconds..."
        sleep 10
      done
      echo "Feast is ready!"
      
      # Test Feast API
      echo "Testing Feast API..."
      curl -f http://{{ .Release.Name }}-feast:{{ .Values.feast.service.port }}/get-online-features || exit 1
      echo "Feast API is accessible!"
{{- end }}

{{/*
Database initialization init container for MLflow
*/}}
{{- define "kornerstone.mlflow.dbInit" -}}
- name: mlflow-db-init
  image: postgres:15-alpine
  command: 
    - 'sh'
    - '-c'
    - |
      echo "Initializing MLflow database..."
      
      # Create MLflow database if it doesn't exist (idempotent)
      if ! PGPASSWORD="${POSTGRES_PASSWORD}" psql -h {{ .Release.Name }}-postgresql -p 5432 -U postgres -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='mlflow'" | grep -q 1; then
        echo "Creating mlflow database..."
        PGPASSWORD="${POSTGRES_PASSWORD}" psql -h {{ .Release.Name }}-postgresql -p 5432 -U postgres -d postgres -c "CREATE DATABASE mlflow;"
      else
        echo "mlflow database already exists."
      fi
      
      # Ensure application user owns mlflow database
      PGPASSWORD="${POSTGRES_PASSWORD}" psql -h {{ .Release.Name }}-postgresql -p 5432 -U postgres -d postgres -c "ALTER DATABASE mlflow OWNER TO {{ .Values.postgresql.auth.username }};" || true
      
      echo "MLflow database initialized successfully!"
  env:
  - name: POSTGRES_PASSWORD
    valueFrom:
      secretKeyRef:
        name: {{ .Release.Name }}-postgresql
        key: postgres-password
{{- end }}

{{/*
MinIO bucket initialization init container
*/}}
{{- define "kornerstone.minio.bucketInit" -}}
- name: minio-bucket-init
  image: minio/mc:latest
  command: 
    - 'sh'
    - '-c'
    - |
      echo "Initializing MinIO buckets..."
      
      # Configure MinIO client
      mc alias set kornerstone http://{{ .Release.Name }}-minio:{{ .Values.minio.service.ports.api }} ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD}
      
      # Create buckets if they don't exist
      mc mb kornerstone/mlflow --ignore-existing
      mc mb kornerstone/feast --ignore-existing
      
      echo "MinIO buckets initialized successfully!"
  env:
  - name: MINIO_ROOT_USER
    valueFrom:
      secretKeyRef:
        name: {{ .Release.Name }}-minio
        key: root-user
  - name: MINIO_ROOT_PASSWORD
    valueFrom:
      secretKeyRef:
        name: {{ .Release.Name }}-minio
        key: root-password
{{- end }} 