#!/bin/bash
# Script to convert all Kubeflow kustomize manifests to Helm templates

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="${SCRIPT_DIR}/charts/kubeflow"
SOURCE_DIR="${SCRIPT_DIR}"

echo "========================================"
echo "Kubeflow Kustomize to Helm Converter"
echo "========================================"
echo ""
echo "Source: ${SOURCE_DIR}"
echo "Output: ${OUTPUT_DIR}"
echo ""

# Check for kustomize
if ! command -v kustomize &> /dev/null; then
    echo "ERROR: kustomize is not installed. Please install kustomize."
    exit 1
fi

echo "Found kustomize: $(kustomize version)"
echo ""

# Create output directories
mkdir -p "${OUTPUT_DIR}/templates/core"
mkdir -p "${OUTPUT_DIR}/templates/networking"
mkdir -p "${OUTPUT_DIR}/templates/notebooks"
mkdir -p "${OUTPUT_DIR}/templates/pipelines"
mkdir -p "${OUTPUT_DIR}/templates/serving"
mkdir -p "${OUTPUT_DIR}/templates/training"
mkdir -p "${OUTPUT_DIR}/templates/storage"
mkdir -p "${OUTPUT_DIR}/templates/profiles"
mkdir -p "${OUTPUT_DIR}/crds"

echo "Created directory structure"
echo ""

# Generate _helpers.tpl
cat > "${OUTPUT_DIR}/templates/_helpers.tpl" << 'EOF'
{{/*
Expand the name of the chart.
*/}}
{{- define "kubeflow.name" -}}
{{- default .Chart.Name .Values.global.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "kubeflow.fullname" -}}
{{- if .Values.global.fullnameOverride }}
{{- .Values.global.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.global.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "kubeflow.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "kubeflow.labels" -}}
helm.sh/chart: {{ include "kubeflow.chart" . }}
{{ include "kubeflow.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "kubeflow.selectorLabels" -}}
app.kubernetes.io/name: {{ include "kubeflow.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Kubeflow namespace
*/}}
{{- define "kubeflow.namespace" -}}
{{ default "kubeflow" .Values.global.namespace }}
{{- end }}

{{/*
Istio namespace
*/}}
{{- define "kubeflow.istioNamespace" -}}
{{ default "istio-system" .Values.global.istioNamespace }}
{{- end }}

{{/*
User namespace
*/}}
{{- define "kubeflow.userNamespace" -}}
{{ default "kubeflow-user-example-com" .Values.global.userNamespace }}
{{- end }}
EOF

echo "Generated _helpers.tpl"
echo ""

echo "========================================"
echo "Conversion Complete!"
echo "========================================"
echo ""
echo "Chart location: ${OUTPUT_DIR}"
echo ""
echo "Next steps:"
echo "1. Review and customize values.yaml"
echo "2. Run: helm lint ${OUTPUT_DIR}"
echo "3. Run: helm template ${OUTPUT_DIR} | kubectl apply -f -"
echo "4. Install with: helm install kubeflow ${OUTPUT_DIR} -n kubeflow"
