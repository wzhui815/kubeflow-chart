#!/usr/bin/env python3
"""
Generate Helm templates from Kubeflow kustomize manifests.
This script processes each kustomize component and generates Helm templates.
"""

import subprocess
from pathlib import Path
import yaml


# Component definitions: (kustomize_path, helm_key, output_file, enabled_by_default)
COMPONENTS = [
    # Infrastructure
    ("common/istio/istio-crds/base", "istioCrds", "networking/istio-crds.yaml", True),
    ("common/istio/istio-namespace/base", "istioNamespace", "networking/istio-namespace.yaml", True),
    ("common/istio/istio-install/overlays/oauth2-proxy", "istio", "networking/istio.yaml", True),
    ("common/istio/cluster-local-gateway/base", "clusterLocalGateway", "networking/cluster-local-gateway.yaml", True),
    ("common/istio/kubeflow-istio-resources/base", "istioResources", "networking/istio-resources.yaml", True),

    # Core infrastructure (auth, cert management)
    ("common/cert-manager/overlays/kubeflow", "certManager", "core/certmanager.yaml", True),
    ("common/oauth2-proxy/overlays/m2m-dex-only", "oauth2Proxy", "core/oauth2-proxy.yaml", True),
    ("common/dex/overlays/oauth2-proxy", "dex", "core/dex.yaml", True),

    # Serving infrastructure
    ("common/knative/knative-serving/overlays/gateways", "knativeServing", "serving/knative-serving.yaml", True),
    ("common/kubeflow-namespace/base", "namespace", "core/namespace.yaml", True),
    ("common/kubeflow-roles/base", "kubeflowRoles", "core/kubeflow-roles.yaml", True),

    # Core
    ("applications/profiles/pss", "profiles", "core/profiles.yaml", True),
    ("applications/centraldashboard/overlays/oauth2-proxy", "centralDashboard", "core/centraldashboard.yaml", True),
    ("applications/admission-webhook/upstream/overlays/cert-manager", "admissionWebhook", "core/admission-webhook.yaml", True),

    # Notebooks
    ("applications/jupyter/notebook-controller/upstream/overlays/kubeflow", "notebookController", "notebooks/notebook-controller.yaml", True),
    ("applications/jupyter/jupyter-web-app/upstream/overlays/istio", "jupyterWebApp", "notebooks/jupyter-web-app.yaml", True),

    # Storage
    ("applications/volumes-web-app/upstream/overlays/istio", "volumesWebApp", "storage/volumes-web-app.yaml", True),
    ("applications/pvcviewer-controller/upstream/base", "pvcviewerController", "storage/pvcviewer-controller.yaml", True),

    # Tensorboards
    ("applications/tensorboard/tensorboard-controller/upstream/overlays/kubeflow", "tensorboardController", "notebooks/tensorboard-controller.yaml", True),
    ("applications/tensorboard/tensorboards-web-app/upstream/overlays/istio", "tensorboardsWebApp", "notebooks/tensorboards-web-app.yaml", True),

    # Training
    #("applications/trainer/overlays", "trainer", "training/trainer.yaml", True),

    # Pipelines
    ("applications/pipeline/overlays", "pipelines", "pipelines/pipelines.yaml", True),

    # Katib
    ("applications/katib/upstream/installs/katib-with-kubeflow", "katib", "training/katib.yaml", True),

    # KServe
    ("applications/kserve/kserve", "kserve", "serving/kserve.yaml", True),
    ("applications/kserve/models-web-app/overlays/kubeflow", "modelsWebApp", "serving/models-web-app.yaml", True),

    # User namespace -> core
    ("common/user-namespace/base", "userNamespace", "core/user-namespace.yaml", True),

    # Optional components (disabled by default)
    # knative-eventing -> serving
    ("common/knative/knative-eventing/base", "knativeEventing", "serving/knative-eventing.yaml", False),
    # training-operator -> training
    ("applications/training-operator/upstream/overlays/kubeflow", "trainingOperator", "training/training-operator.yaml", False),
    # spark-operator -> training
    ("applications/spark/spark-operator/overlays/kubeflow", "sparkOperator", "training/spark-operator.yaml", False),
]

HELPERS_TPL = '''{{- /*
Kubeflow Helm Chart Helpers
*/ -}}

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
'''

def run_kustomize_build(path):
    """Run kustomize build and return the output."""
    try:
        print(f"    Running: kustomize build {path}")
        result = subprocess.run(
            ["kustomize", "build", path],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"    Error: {e.stderr[:200]}")
        return ""

def main():
    print("=" * 70)
    print("Kubeflow Kustomize to Helm Converter")
    print("=" * 70)
    print()

    base_dir = Path("/root/manifests")
    output_base = base_dir / "helm" / "charts" / "kubeflow"

    # Write _helpers.tpl
    helpers_path = output_base / "templates" / "_helpers.tpl"
    with open(helpers_path, "w") as f:
        f.write(HELPERS_TPL)
    print(f"Generated: templates/_helpers.tpl")
    print()

    total_components = len(COMPONENTS)
    processed = 0
    errors = 0

    for kustomize_path, helm_key, output_file, enabled in COMPONENTS:
        processed += 1
        full_path = base_dir / "kustomize" / kustomize_path

        print(f"[{processed}/{total_components}] Processing: {helm_key}")
        print(f"    Source: {kustomize_path}")

        if not full_path.exists():
            print(f"    Warning: Path does not exist, skipping")
            errors += 1
            continue

        # Run kustomize build
        manifests = run_kustomize_build(str(full_path))

        if not manifests.strip():
            print(f"    Warning: No manifests generated")
            continue

        # Write raw manifests to output file with Helm condition
        output_path = output_base / "templates" / output_file
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            f.write(f"{{- /*\n")
            f.write(f"  {helm_key} component\n")
            f.write(f"  Source: {kustomize_path}\n")
            f.write(f"  Enabled by default: {enabled}\n")
            f.write(f"*/ -}}\n\n")
            f.write(f"{{- if .Values.{helm_key}.enabled }}\n\n")
            f.write(manifests)
            f.write(f"\n{{- end }}\n")

        # Count documents
        doc_count = len([doc for doc in yaml.safe_load_all(manifests) if doc])
        print(f"    Written: templates/{output_file} ({doc_count} documents)")

    print()
    print("=" * 70)
    print("Conversion Complete!")
    print("=" * 70)
    print()
    print(f"Total components: {total_components}")
    print(f"Processed: {processed}")
    print(f"Errors: {errors}")
    print()
    print(f"Chart location: {output_base}")
    print()
    print("Next steps:")
    print("1. Review and customize values.yaml")
    print("2. Run: helm lint charts/kubeflow")
    print("3. Run: helm template charts/kubeflow | kubectl apply -f -")
    print("4. Install with: helm install kubeflow charts/kubeflow -n kubeflow")

if __name__ == "__main__":
    main()
