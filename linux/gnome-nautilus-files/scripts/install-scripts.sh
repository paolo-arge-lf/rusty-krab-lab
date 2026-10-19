#!/bin/bash
set -euo

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
destination="$HOME/.local/share/nautilus/scripts"

install -d -m 755 "$destination"
install -m 755 "$script_dir/Open in VS Code" "$destination/Open in VS Code"