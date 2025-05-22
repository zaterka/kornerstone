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
  command: ['sh', '-c', 'until pg_isready -h {{ .Release.Name }}-postgresql -p 5432; do echo waiting for postgres; sleep 2; done;']
  env:
  - name: PGPASSWORD
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
  image: alpine:3.14
  command: ['sh', '-c', 'until nc -z {{ .Release.Name }}-minio {{ .Values.minio.service.ports.api }}; do echo waiting for minio; sleep 2; done;']
{{- end }}

{{/*
Common init containers for waiting on MLflow
*/}}
{{- define "kornerstone.mlflow.initContainer" -}}
- name: wait-for-mlflow
  image: curlimages/curl:7.82.0
  command: ['sh', '-c', 'until curl -s http://{{ .Release.Name }}-mlflow:{{ .Values.mlflow.service.port }}; do echo waiting for mlflow; sleep 2; done;']
{{- end }}

{{/*
Common init containers for waiting on Feast
*/}}
{{- define "kornerstone.feast.initContainer" -}}
- name: wait-for-feast
  image: alpine:3.14
  command: ['sh', '-c', 'until nc -z {{ .Release.Name }}-feast {{ .Values.feast.service.port }}; do echo waiting for feast; sleep 2; done;']
{{- end }} 