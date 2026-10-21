#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
install_dir="$script_dir/.deps/freecad-mcp-bridge"
repository="https://github.com/CREATeNG/freecad-mcp-bridge.git"
version="v0.1.23"
revision="81a73e41ed3235c55a3f06d4803b7c556fa39b97"

command -v git >/dev/null 2>&1 || {
    echo "Git is required to install MCP Bridge." >&2
    exit 1
}

if [[ -e "$install_dir" || -L "$install_dir" ]]; then
    if [[ -d "$install_dir/.git" ]] &&
        [[ "$(git -C "$install_dir" rev-parse HEAD)" == "$revision" ]] &&
        [[ -z "$(git -C "$install_dir" status --porcelain)" ]]; then
        echo "MCP Bridge $version is already installed at $install_dir"
        exit 0
    fi
    echo "Existing installation differs from $version; leaving it untouched: $install_dir" >&2
    exit 1
fi

mkdir -p -- "$script_dir/.deps"
download_dir="$(mktemp -d "$script_dir/.deps/mcp-bridge.XXXXXXXX")"
trap 'rm -rf -- "$download_dir"' EXIT

git -c advice.detachedHead=false clone --depth 1 --branch "$version" \
    "$repository" "$download_dir/source"

if [[ "$(git -C "$download_dir/source" rev-parse HEAD)" != "$revision" ]]; then
    echo "Release revision does not match the pinned commit; installation aborted." >&2
    exit 1
fi

mv -- "$download_dir/source" "$install_dir"
echo "Installed MCP Bridge $version at $install_dir"
