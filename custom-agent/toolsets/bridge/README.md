# MK2 Bridge (V8)

JavaScript MCP server providing hard bridge capabilities for system visibility.

## Requirements

- Node.js >= 20.0.0 (V8 engine)
- No dependencies — pure Node.js

## Usage

### Via MCP (VS Code integration)

The bridge is configured in `.vscode/mcp.json` as `mk2-bridge`. VS Code will start it automatically.

### Direct execution

```bash
cd bridge
node server.js
```

### CLI test

```bash
# Test initialization
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | node bridge/server.js

# List available tools
echo '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' | node bridge/server.js

# Get system info
echo '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"system_info","arguments":{}}}' | node bridge/server.js

# List processes
echo '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"list_processes","arguments":{"limit":20}}}' | node bridge/server.js
```

## Available Tools

| Tool | Description |
|------|-------------|
| `system_info` | OS, CPU, memory, uptime, network interfaces, V8 version |
| `list_processes` | Running processes with PID, CPU, memory. Filter by pattern |
| `network_connections` | Active connections with local/remote addresses, states |
| `watch_directory` | Directory contents with metadata (size, mtime, permissions) |
| `exec_command` | Execute shell commands (careful with this one) |
| `read_binary` | Hex dump of binary files for analysis |
| `find_files` | Search by name pattern, content, or modified date |
| `hash_file` | MD5, SHA1, SHA256 hashes for file integrity |

## Why V8

The bridge runs on V8 (Node.js) for:
- Native system API access (child_process, fs, crypto)
- Real-time process monitoring
- Binary file analysis
- Cross-platform support (Windows/Linux)
- No external dependencies to compromise

## Architecture

```
┌─────────────────┐      stdio      ┌─────────────────┐
│   VS Code       │ ◄────────────► │  mk2-bridge     │
│   (MCP Client)  │    JSON-RPC    │  (V8/Node.js)   │
└─────────────────┘                 └────────┬────────┘
                                             │
                                    ┌────────▼────────┐
                                    │  System APIs    │
                                    │  - child_process│
                                    │  - fs           │
                                    │  - crypto       │
                                    │  - os           │
                                    └─────────────────┘
```

## Security Notes

- `exec_command` can run arbitrary commands — use carefully
- Path traversal is not restricted — the bridge trusts you
- No authentication — designed for local use only
