# FreeCAD MCP

This project uses [MCP Bridge](https://github.com/CREATeNG/freecad-mcp-bridge)
to let Codex work with a running FreeCAD session over Streamable HTTP.
The add-on runs inside FreeCAD and needs no separate Python environment or
Node.js relay.

## Install

Requirements: Linux, Bash, Git, and FreeCAD **1.1 or newer**. The launcher supports
native FreeCAD installations and the `org.freecad.FreeCAD` Flatpak.

From the repository root:

```bash
bash FreeCad/install-mcp-bridge.sh
```

The installer downloads upstream release **v0.1.23** and checks its commit against
`81a73e41ed3235c55a3f06d4803b7c556fa39b97`. It installs under
`FreeCad/.deps/freecad-mcp-bridge/`, which Git ignores. Running it again accepts
an unchanged installation at that revision and refuses to overwrite a different
or modified checkout. To upgrade, review a new upstream release and update both
the tag and commit in the installer. Close FreeCAD, move the old
`.deps/freecad-mcp-bridge/` checkout aside, then run the installer again.

## Start and connect

1. Save your work and close existing FreeCAD windows, then launch a project
   session:

   ```bash
   bash FreeCad/start-freecad.sh FreeCad/FreeCAD-3D-Pencil-Printable.FCStd
   ```

   Omit the model path to start without opening a document. The launcher resolves
   the add-on relative to itself, passes it through FreeCAD's `--module-path`,
   and forwards other arguments. For an AppImage or another executable, use:

   ```bash
   FREECAD_BIN=/absolute/path/to/FreeCAD.AppImage bash FreeCad/start-freecad.sh
   ```

2. Click **MCP Bridge On/Off** in FreeCAD's toolbar, or **MCP: Off** in its status
   bar. The bridge starts only when toggled on, each session. Its default endpoint
   is `http://127.0.0.1:39280/mcp`.
3. Open this trusted project in Codex and restart its MCP connection or start a
   new Codex session after enabling the bridge. The project configuration in
   [`.codex/config.toml`](../.codex/config.toml) registers:

   ```toml
   [mcp_servers.freecad]
   url = "http://127.0.0.1:39280/mcp"
   ```

   Codex loads project configuration only for trusted projects; see the
   [official OpenAI MCP documentation](https://developers.openai.com/codex/mcp/).

## Verify

From the repository root, check registration and run a read-only request:

```bash
codex mcp get freecad
python3 FreeCad/.deps/freecad-mcp-bridge/send_cmd.py 39280 'print(App.Version()); print(list(App.listDocuments()))'
```

The first command verifies configuration only. The second requires the bridge
to be on and prints the FreeCAD version and open document names. Codex should
discover `execute_python`, `execute_python_file`, and `get_output_page`.

If connection fails, check that FreeCAD was started with the project launcher
and the bridge is on. If you change the port under **Edit → Preferences → MCP
Bridge**, update `.codex/config.toml` and the verification command to match.
Only one FreeCAD session can listen on a given port.

## Local access and shutdown

The bridge binds to `127.0.0.1` and has no authentication. Other local processes
can reach it while it is on. Its tools execute Python with FreeCAD's permissions
and access to its open documents; the bridge does not sandbox that code. Review
tool calls using your MCP client's approval controls and keep private models out
of requests you do not intend to share with your AI provider. See
[upstream security guidance](https://github.com/CREATeNG/freecad-mcp-bridge/blob/v0.1.23/SECURITY.md).

Click the toggle again to stop the bridge, or exit FreeCAD. The add-on is loaded
for sessions started by this launcher; nothing is installed into your user-wide
FreeCAD `Mod` directory.
