#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
K8S_MANIFESTS_FILENAME="$SCRIPT_DIR/rusty-krab-lab-k8s-manifests.yaml"

if [[ $EUID -ne 0 ]]; then
  echo "Error: This script must be run as root (sudo)." >&2
  exit 1
fi

if ! command -v podman >/dev/null 2>&1; then
  echo "Error: podman is not installed or not in PATH." >&2
  exit 1
fi

if [[ ! -f "$K8S_MANIFESTS_FILENAME" ]]; then
  echo "Error: rusty-krab-lab-k8s-manifests.yaml is missing." >&2
  exit 1
fi

# Omit --force so the PVC-backed configuration, recordings, and cache volumes
# remain available for the next launch. The frigate-env secret is also retained.
echo "podman kube down $K8S_MANIFESTS_FILENAME"
podman kube down "$K8S_MANIFESTS_FILENAME"
