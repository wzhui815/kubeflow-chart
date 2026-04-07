# Kubeflow Helm Charts

This directory contains Helm charts for deploying Kubeflow on Kubernetes.

## Overview

These Helm charts are generated from the official Kubeflow manifests repository (https://github.com/kubeflow/manifests). The charts provide a Helm-based installation alternative to the native kustomize-based deployment.

## Chart Structure

### kubeflow/
The main Kubeflow platform chart that includes all components for a complete ML platform.

```
kubeflow/
├── Chart.yaml          # Chart metadata
├── values.yaml         # Default configuration values
├── templates/          # Kubernetes resource templates
│   ├── _helpers.tpl    # Helm helper templates
│   ├── core/           # Core infrastructure components
│   ├── networking/     # Networking and service mesh
│   ├── notebooks/      # Jupyter notebooks and TensorBoard
│   ├── pipelines/      # Kubeflow Pipelines
│   ├── serving/        # Model serving (KServe, Knative)
│   ├── storage/        # Storage and volumes
│   └── training/       # Training operators (Katib, Trainer)
└── crds/               # Custom Resource Definitions
```

## Directory Organization

### core/
Core infrastructure components essential for Kubeflow operation:
- **certmanager.yaml** - TLS certificate management
- **namespace.yaml** - Kubeflow namespace and user namespace
- **kubeflow-roles.yaml** - RBAC roles and bindings
- **dex.yaml** - Dex identity provider for authentication
- **oauth2-proxy.yaml** - OAuth2 proxy for authentication
- **profiles.yaml** - Profile controller for multi-tenancy
- **centraldashboard.yaml** - Kubeflow central dashboard
- **admission-webhook.yaml** - Pod defaults admission webhook
- **user-namespace.yaml** - Default user namespace

### networking/
Networking infrastructure and service mesh:
- **istio-crds.yaml** - Istio Custom Resource Definitions
- **istio-namespace.yaml** - Istio system namespace
- **istio.yaml** - Istio service mesh components
- **istio-resources.yaml** - Istio resources for Kubeflow
- **cluster-local-gateway.yaml** - Cluster-local gateway

### notebooks/
Jupyter notebooks and TensorBoard components:
- **notebook-controller.yaml** - Notebook controller
- **jupyter-web-app.yaml** - Jupyter web application
- **tensorboard-controller.yaml** - TensorBoard controller
- **tensorboards-web-app.yaml** - TensorBoard web application

### pipelines/
Kubeflow Pipelines components:
- **pipelines.yaml** - Complete Kubeflow Pipelines installation

### serving/
Model serving components:
- **kserve.yaml** - KServe for model serving
- **models-web-app.yaml** - Models web application
- **knative-serving.yaml** - Knative serving for serverless
- **knative-eventing.yaml** - Knative eventing (optional)

### storage/
Storage and volume management:
- **volumes-web-app.yaml** - Volumes web application
- **pvcviewer-controller.yaml** - PVC viewer controller

### training/
Training and experimentation components:
- **katib.yaml** - Katib for hyperparameter tuning
- **trainer.yaml** - Kubeflow Trainer (v2)
- **training-operator.yaml** - Training Operator v1 (optional)
- **spark-operator.yaml** - Spark Operator (optional)

## Installation

### Prerequisites
- Kubernetes cluster (1.29+)
- Helm 3.0+
- kubectl configured

### Quick Start

```bash
# Add the Kubeflow Helm repository (when published)
# helm repo add kubeflow https://kubeflow.github.io/charts

# Install Kubeflow
helm install kubeflow ./kubeflow -n kubeflow --create-namespace
```

### Custom Configuration

Create a `custom-values.yaml` file:

```yaml
# Disable optional components
knativeEventing:
  enabled: false

trainingOperator:
  enabled: false

sparkOperator:
  enabled: false

# Configure ingress
global:
  istioNamespace: istio-system
```

Install with custom values:

```bash
helm install kubeflow ./kubeflow -n kubeflow --create-namespace -f custom-values.yaml
```

## Configuration

See `values.yaml` for all available configuration options. Key sections include:

- `global.*` - Global settings (namespaces, security)
- `certManager.*` - Certificate management
- `istio.*` - Service mesh configuration
- `dex.*` - Authentication settings
- `profiles.*` - Multi-tenancy configuration
- `pipelines.*` - Kubeflow Pipelines settings
- `katib.*` - Hyperparameter tuning
- `kserve.*` - Model serving

## Upgrading

```bash
# Upgrade to a new version
helm upgrade kubeflow ./kubeflow -n kubeflow

# Upgrade with new values
helm upgrade kubeflow ./kubeflow -n kubeflow -f new-values.yaml
```

## Uninstallation

```bash
# Uninstall Kubeflow
helm uninstall kubeflow -n kubeflow

# Clean up CRDs (optional, be careful)
kubectl delete crd -l app=kubeflow
```

## Troubleshooting

### Check Component Status

```bash
# Check all pods
kubectl get pods -n kubeflow

# Check Istio pods
kubectl get pods -n istio-system

# Check cert-manager
kubectl get pods -n cert-manager
```

### Common Issues

1. **Image pull errors**: Check image registry access
2. **Pending pods**: Check resource quotas and node capacity
3. **Istio issues**: Verify CNI compatibility
4. **Auth issues**: Check Dex and OAuth2 configuration

## Contributing

To regenerate the Helm charts from the Kubeflow manifests:

```bash
# Run the conversion script
python3 generate_helm_templates.py
```

## License

These Helm charts follow the same license as the Kubeflow project (Apache 2.0).

## Resources

- [Kubeflow Documentation](https://www.kubeflow.org/docs/)
- [Kubeflow Manifests Repository](https://github.com/kubeflow/manifests)
- [Helm Documentation](https://helm.sh/docs/)
