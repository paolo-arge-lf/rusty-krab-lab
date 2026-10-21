#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
bridge_dir="$script_dir/.deps/freecad-mcp-bridge"

if [[ ! -f "$bridge_dir/freecad/mcp_bridge/init_gui.py" ]]; then
    echo "MCP Bridge is missing. Run: bash \"$script_dir/install-mcp-bridge.sh\"" >&2
    exit 1
fi

if [[ -n "${FREECAD_BIN:-}" ]]; then
    exec "$FREECAD_BIN" --module-path "$bridge_dir" "$@"
elif command -v FreeCAD >/dev/null 2>&1; then
    exec FreeCAD --module-path "$bridge_dir" "$@"
elif command -v freecad >/dev/null 2>&1; then
    exec freecad --module-path "$bridge_dir" "$@"
elif command -v flatpak >/dev/null 2>&1 && flatpak info org.freecad.FreeCAD >/dev/null 2>&1; then
    exec flatpak run org.freecad.FreeCAD --module-path "$bridge_dir" "$@"
else
    echo "FreeCAD 1.1 or newer is required. Install it or set FREECAD_BIN to its executable." >&2
    exit 1
fi
