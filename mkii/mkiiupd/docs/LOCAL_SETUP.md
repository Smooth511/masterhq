# Local Setup Guide

This guide covers running the Claude-MKII MCP servers, bridge, CLI, and Docker environment locally.

---

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.11+ | For MCP server + CLI |
| Node.js | 20+ | For the V8 bridge server |
| pip | latest | `pip install --upgrade pip` |
| Docker + Compose | v2+ | Optional — for containerised mode |
| VS Code | 1.99+ | For MCP / Copilot Chat integration |

---

## Quick Start — Install Everything

```bash
git clone https://github.com/Smooth115/Claude-MKII.git
cd Claude-MKII

# Python deps (MCP server + CLI + tools)
pip install -r mcp-server/requirements.txt -r cli/requirements.txt -r tools/requirements.txt

# Bridge has zero deps — just needs Node.js 20+
node --version  # confirm >= 20
```

Or use the VS Code task: **Terminal → Run Task → MK2: Install Dependencies**

---

## VS Code Integration (MCP)

This is the main way to use the project. VS Code connects to the MCP servers and exposes their tools to Copilot Chat.

### What's configured

`.vscode/mcp.json` defines three MCP server entries:

| Server | Transport | Runtime | What it does |
|--------|-----------|---------|--------------|
| `claude-mkii` | stdio | Python | Project file tools — read, search, list, logs, status |
| `mk2-bridge` | stdio | Node.js (V8) | System tools — processes, network, binary analysis, exec |
| `claude-mkii-docker` | stdio | Docker | Same as `claude-mkii` but containerised |

### Getting it running

1. Open the repo folder in VS Code.
2. VS Code should auto-detect `.vscode/mcp.json` and show MCP servers.
3. Open the **Command Palette** (`Ctrl+Shift+P` / `Cmd+Shift+P`).
4. Run **"MCP: List Servers"** — you should see `claude-mkii` and `mk2-bridge`.
5. Start them (VS Code may auto-start them on first Copilot Chat use).

> **Requires:** VS Code ≥ 1.99 + GitHub Copilot + GitHub Copilot Chat extensions.
> Recommended extensions are listed in `.vscode/extensions.json` — VS Code will prompt to install them.

### Available tools

**claude-mkii** (Python MCP server):

| Tool | Description |
|------|-------------|
| `read_file` | Read any file from the project |
| `list_directory` | List contents of a directory |
| `search_files` | Full-text search across project files |
| `read_logs` | Read markdown files from log/evidence directories |
| `project_status` | Return a project structure summary |

**mk2-bridge** (Node.js V8 bridge):

| Tool | Description |
|------|-------------|
| `system_info` | OS, CPU, memory, uptime, network interfaces |
| `list_processes` | Running processes with PID, CPU, memory. Filter by pattern |
| `network_connections` | Active connections with local/remote addresses, states |
| `watch_directory` | Directory contents with metadata (size, mtime, permissions) |
| `exec_command` | Execute shell commands |
| `read_binary` | Hex dump of binary files for analysis |
| `find_files` | Search by name pattern, content, or modified date |
| `hash_file` | MD5, SHA1, SHA256 hashes for file integrity |

---

## CLI Usage

```bash
# Project overview
python3 cli/mk2_cli.py status

# Read a file
python3 cli/mk2_cli.py read README.md

# Search project files
python3 cli/mk2_cli.py search "rootkit"

# Read all log directories
python3 cli/mk2_cli.py logs

# Read only the most recently modified file per directory
python3 cli/mk2_cli.py logs --recent

# Read a specific directory
python3 cli/mk2_cli.py logs evidence

# Start the MCP server from CLI
python3 cli/mk2_cli.py serve
```

---

## Docker (Optional)

### Build and run

```bash
docker compose build
docker compose up mcp-server
```

### CLI via Docker

```bash
docker compose run --rm cli python /project/cli/mk2_cli.py status
```

The project directory is bind-mounted into the container at `/project`.

---

## VS Code Tasks

Pre-built tasks are available via **Terminal → Run Task**:

| Task | What it does |
|------|-------------|
| MK2 Bridge: Start | Starts the Node.js V8 bridge server |
| MK2 MCP Server: Start | Starts the Python MCP server |
| MK2 CLI: Status | Runs `mk2_cli.py status` |
| MK2 CLI: Search | Prompts for a search query, runs search |
| MK2: Install Dependencies | Installs all Python dependencies |
| MK2 Docker: Start | Starts MCP server via Docker Compose |

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'mcp'`

```bash
pip install -r mcp-server/requirements.txt
```

### VS Code does not show MCP servers

- VS Code ≥ 1.99 required.
- GitHub Copilot + Copilot Chat extensions must be installed.
- Check `.vscode/mcp.json` exists in the workspace root.
- Open the Output panel → select **"MCP"** to view server logs.

### Bridge server won't start

- Requires Node.js ≥ 20. Check with `node --version`.
- Test manually: `echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | node bridge/server.js`

### `python: command not found` (outside Docker)

Use `python3` instead of `python`:

```bash
python3 mcp-server/server.py
```

### `Path escapes the project root` error

All file tool paths must be **relative** to the repo root. Use `README.md`, not `/home/user/Claude-MKII/README.md`.

---

## Project Structure

```
Claude-MKII/
├── .vscode/
│   ├── mcp.json           # MCP server configuration
│   ├── settings.json      # Workspace settings
│   ├── tasks.json         # VS Code tasks
│   └── extensions.json    # Recommended extensions
├── mcp-server/
│   ├── server.py          # Python MCP server (FastMCP, stdio)
│   └── requirements.txt
├── bridge/
│   ├── server.js          # Node.js V8 bridge server (MCP, stdio)
│   ├── package.json
│   └── README.md
├── cli/
│   ├── mk2_cli.py         # CLI entry point
│   └── requirements.txt
├── tools/
│   ├── parse_evtx.py      # EVTX log parser
│   ├── safe_read.py       # Safe file reader
│   └── requirements.txt
├── core/                  # Core documentation / memory files
├── evidence/              # Investigation evidence
├── investigation/         # Investigation reports
├── logs/                  # Log files
├── mk2-phantom/           # Phantom vault
├── Dockerfile
├── docker-compose.yml
└── .dockerignore
```
