# Repository Guidelines

## Project Structure & Module Organization

Rusty Krab Lab is an experimental collection of Linux utilities, assets, and lab configuration. It currently has no Rust crate, application entry point, or dedicated test directory.

- `README.md` contains an embedded Space Shuttle STL model and a Mermaid SDLC diagram; preserve the large geometry block during documentation edits.
- `linux/gnome-nautilus-files/scripts/` holds the Nautilus “Open in VS Code” action and its installer.
- `linux/folder-icons/` contains SVG icons.
- `podman/` contains local Kubernetes-style manifests for Ollama and Open WebUI, plus lifecycle scripts.
- `.vscode/` defines editor formatting and extension recommendations. `FreeCad/` documents the project-local FreeCAD MCP environment; `tools/` is currently empty.

## Build, Test, and Development Commands

There is no repository-wide build command or package manager configuration. Run commands from the repository root unless noted:

- `bash -n linux/gnome-nautilus-files/scripts/*.sh 'linux/gnome-nautilus-files/scripts/Open in VS Code' podman/*.sh` checks Bash syntax without executing scripts.
- `bash linux/gnome-nautilus-files/scripts/install-scripts.sh` installs the Nautilus action under `~/.local/share/nautilus/scripts`.
- From `podman/`, `bash podman-kube-play.sh` launches or replaces the lab workloads; it requires Podman and rejects root execution.
- `git diff --check` detects whitespace errors before review.

## Coding Style & Naming Conventions

VS Code enables format-on-save with Prettier and selects rust-analyzer for future Rust files; no CLI formatter or lint pipeline is configured. Use two-space YAML indentation and match surrounding Bash formatting. For new Bash scripts, use `set -euo pipefail`, quote path expansions, and resolve resources relative to the script. Prefer descriptive, hyphenated filenames; preserve the Nautilus action’s display name.

## Testing Guidelines

No automated framework or coverage threshold is configured. Run syntax checks, then manually verify affected behavior in a disposable environment. For Nautilus changes, check directory selection, file selection, and paths containing spaces. Preview changed SVGs and Markdown diagrams. Record commands and observed results in the pull request.

## Commit & Pull Request Guidelines

History uses brief, informal subjects with no consistent convention. Write descriptive imperative subjects, such as `Fix Nautilus folder selection`, and keep commits focused. Pull requests should explain purpose, affected paths, validation, and related issues when applicable. Include screenshots for visual changes.

## Security & Configuration

Favor simple, evidence-backed changes and protect private data. Keep credentials outside tracked manifests. Review exposed ports, GPU device mounts, and persistent volumes before running workloads. The Podman start and stop scripts currently require different privilege contexts; verify ownership before teardown and avoid deleting persistent data.
