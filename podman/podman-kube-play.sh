#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
K8S_MANIFESTS_FILENAME="rusty-krab-lab-k8s-manifests.yaml"

if [[ $EUID -eq 0 ]]; then
    echo "Error: This script must not be run with sudo." >&2
    exit 1
fi

if ! command -v podman >/dev/null 2>&1; then
  echo "Error: podman is not installed or not in PATH." >&2
  exit 1
fi

echo "podman kube play $K8S_MANIFESTS_FILENAME --replace"
podman kube play $K8S_MANIFESTS_FILENAME --replace