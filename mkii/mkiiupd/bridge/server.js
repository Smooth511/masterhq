#!/usr/bin/env node
/**
 * Claude-MK2 Bridge Server (V8)
 * 
 * JavaScript MCP server providing hard bridge capabilities:
 * - Process visibility and monitoring
 * - Real-time system observation
 * - Network connection tracking
 * - File system monitoring
 * - Registry key observation (Windows)
 * 
 * Runs on V8 (Node.js) for native system access.
 * Communicates via stdio (MCP protocol).
 */

import { createInterface } from 'readline';
import { spawn, execSync } from 'child_process';
import { readFileSync, writeFileSync, existsSync, readdirSync, statSync } from 'fs';
import { join, resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import { platform, hostname, cpus, totalmem, freemem, uptime, networkInterfaces } from 'os';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const PROJECT_ROOT = resolve(__dirname, '..');

// MCP Protocol constants
const JSONRPC_VERSION = '2.0';

// Server info
const SERVER_INFO = {
  name: 'mk2-bridge',
  version: '1.0.0',
  capabilities: {
    tools: {},
    resources: {},
    prompts: {}
  }
};

// Tool definitions
const TOOLS = {
  // System visibility tools
  'system_info': {
    description: 'Get comprehensive system information including OS, CPU, memory, uptime',
    inputSchema: {
      type: 'object',
      properties: {},
      required: []
    }
  },
  'list_processes': {
    description: 'List running processes with PID, name, CPU, memory usage. Use pattern to filter.',
    inputSchema: {
      type: 'object',
      properties: {
        pattern: {
          type: 'string',
          description: 'Optional regex pattern to filter process names'
        },
        limit: {
          type: 'number',
          description: 'Max number of processes to return (default: 50)'
        }
      },
      required: []
    }
  },
  'network_connections': {
    description: 'List active network connections with local/remote addresses and states',
    inputSchema: {
      type: 'object',
      properties: {
        state: {
          type: 'string',
          description: 'Filter by connection state (ESTABLISHED, LISTEN, etc.)'
        }
      },
      required: []
    }
  },
  'watch_directory': {
    description: 'Get directory contents with metadata (size, modified time, permissions)',
    inputSchema: {
      type: 'object',
      properties: {
        path: {
          type: 'string',
          description: 'Directory path to watch'
        },
        recursive: {
          type: 'boolean',
          description: 'Include subdirectories (default: false)'
        }
      },
      required: ['path']
    }
  },
  'exec_command': {
    description: 'Execute a shell command and return output. Use carefully.',
    inputSchema: {
      type: 'object',
      properties: {
        command: {
          type: 'string',
          description: 'Command to execute'
        },
        timeout: {
          type: 'number',
          description: 'Timeout in milliseconds (default: 30000)'
        }
      },
      required: ['command']
    }
  },
  'read_binary': {
    description: 'Read file as hex dump for binary analysis',
    inputSchema: {
      type: 'object',
      properties: {
        path: {
          type: 'string',
          description: 'File path to read'
        },
        offset: {
          type: 'number',
          description: 'Start offset in bytes (default: 0)'
        },
        length: {
          type: 'number',
          description: 'Number of bytes to read (default: 256)'
        }
      },
      required: ['path']
    }
  },
  'find_files': {
    description: 'Search for files by name pattern, content, or metadata',
    inputSchema: {
      type: 'object',
      properties: {
        directory: {
          type: 'string',
          description: 'Directory to search in'
        },
        pattern: {
          type: 'string',
          description: 'Filename pattern (glob or regex)'
        },
        content: {
          type: 'string',
          description: 'Search for files containing this text'
        },
        modified_after: {
          type: 'string',
          description: 'ISO date string - files modified after this date'
        }
      },
      required: ['directory']
    }
  },
  'hash_file': {
    description: 'Calculate cryptographic hashes (MD5, SHA1, SHA256) for a file',
    inputSchema: {
      type: 'object',
      properties: {
        path: {
          type: 'string',
          description: 'File path to hash'
        }
      },
      required: ['path']
    }
  }
};

// Tool implementations
const toolHandlers = {
  system_info: async () => {
    const nets = networkInterfaces();
    const interfaces = {};
    for (const [name, addrs] of Object.entries(nets)) {
      interfaces[name] = addrs
        .filter(a => !a.internal)
        .map(a => ({ address: a.address, family: a.family, mac: a.mac }));
    }
    
    return {
      platform: platform(),
      hostname: hostname(),
      cpus: cpus().length,
      cpu_model: cpus()[0]?.model || 'unknown',
      total_memory_gb: (totalmem() / 1024 / 1024 / 1024).toFixed(2),
      free_memory_gb: (freemem() / 1024 / 1024 / 1024).toFixed(2),
      uptime_hours: (uptime() / 3600).toFixed(2),
      node_version: process.version,
      v8_version: process.versions.v8,
      network_interfaces: interfaces
    };
  },

  list_processes: async (args) => {
    const limit = args.limit || 50;
    const pattern = args.pattern ? new RegExp(args.pattern, 'i') : null;
    
    try {
      let output;
      if (platform() === 'win32') {
        output = execSync('tasklist /FO CSV /NH', { encoding: 'utf8', timeout: 10000 });
        const lines = output.trim().split('\n');
        const processes = lines.map(line => {
          const parts = line.split('","').map(p => p.replace(/"/g, ''));
          return {
            name: parts[0],
            pid: parseInt(parts[1]) || 0,
            session: parts[2],
            memory_kb: parseInt(parts[4]?.replace(/[, K]/g, '')) || 0
          };
        });
        const filtered = pattern 
          ? processes.filter(p => pattern.test(p.name))
          : processes;
        return filtered.slice(0, limit);
      } else {
        output = execSync('ps aux --no-headers', { encoding: 'utf8', timeout: 10000 });
        const lines = output.trim().split('\n');
        const processes = lines.map(line => {
          const parts = line.trim().split(/\s+/);
          return {
            user: parts[0],
            pid: parseInt(parts[1]) || 0,
            cpu: parseFloat(parts[2]) || 0,
            mem: parseFloat(parts[3]) || 0,
            vsz: parseInt(parts[4]) || 0,
            rss: parseInt(parts[5]) || 0,
            command: parts.slice(10).join(' ')
          };
        });
        const filtered = pattern
          ? processes.filter(p => pattern.test(p.command))
          : processes;
        return filtered.slice(0, limit);
      }
    } catch (err) {
      return { error: err.message };
    }
  },

  network_connections: async (args) => {
    try {
      let output;
      if (platform() === 'win32') {
        output = execSync('netstat -ano', { encoding: 'utf8', timeout: 10000 });
      } else {
        output = execSync('netstat -tunapl 2>/dev/null || ss -tunapl', { encoding: 'utf8', timeout: 10000 });
      }
      
      const lines = output.trim().split('\n').slice(2); // Skip headers
      const connections = lines.map(line => {
        const parts = line.trim().split(/\s+/);
        return {
          proto: parts[0],
          local: parts[3] || parts[1],
          remote: parts[4] || parts[2],
          state: parts[5] || parts[3],
          pid: parts[6] || parts[4]
        };
      });
      
      if (args.state) {
        return connections.filter(c => c.state?.toUpperCase() === args.state.toUpperCase());
      }
      return connections;
    } catch (err) {
      return { error: err.message };
    }
  },

  watch_directory: async (args) => {
    const targetPath = resolve(args.path);
    
    if (!existsSync(targetPath)) {
      return { error: `Path does not exist: ${targetPath}` };
    }
    
    const stat = statSync(targetPath);
    if (!stat.isDirectory()) {
      return { error: `Not a directory: ${targetPath}` };
    }
    
    const entries = [];
    const walkDir = (dir, depth = 0) => {
      if (!args.recursive && depth > 0) return;
      
      try {
        const items = readdirSync(dir);
        for (const item of items) {
          const fullPath = join(dir, item);
          try {
            const st = statSync(fullPath);
            entries.push({
              path: fullPath,
              name: item,
              type: st.isDirectory() ? 'directory' : 'file',
              size: st.size,
              modified: st.mtime.toISOString(),
              mode: st.mode.toString(8)
            });
            if (st.isDirectory() && args.recursive) {
              walkDir(fullPath, depth + 1);
            }
          } catch (e) {
            entries.push({ path: fullPath, name: item, error: e.message });
          }
        }
      } catch (e) {
        return { error: e.message };
      }
    };
    
    walkDir(targetPath);
    return { directory: targetPath, count: entries.length, entries };
  },

  exec_command: async (args) => {
    const timeout = args.timeout || 30000;
    
    try {
      const output = execSync(args.command, {
        encoding: 'utf8',
        timeout,
        maxBuffer: 10 * 1024 * 1024 // 10MB
      });
      return { success: true, output: output.trim() };
    } catch (err) {
      return {
        success: false,
        error: err.message,
        stderr: err.stderr?.toString() || '',
        stdout: err.stdout?.toString() || ''
      };
    }
  },

  read_binary: async (args) => {
    const targetPath = resolve(args.path);
    const offset = args.offset || 0;
    const length = args.length || 256;
    
    if (!existsSync(targetPath)) {
      return { error: `File does not exist: ${targetPath}` };
    }
    
    try {
      const buffer = readFileSync(targetPath);
      const slice = buffer.slice(offset, offset + length);
      
      // Format as hex dump
      const lines = [];
      for (let i = 0; i < slice.length; i += 16) {
        const chunk = slice.slice(i, i + 16);
        const hex = [...chunk].map(b => b.toString(16).padStart(2, '0')).join(' ');
        const ascii = [...chunk].map(b => (b >= 32 && b < 127) ? String.fromCharCode(b) : '.').join('');
        lines.push(`${(offset + i).toString(16).padStart(8, '0')}  ${hex.padEnd(48)}  ${ascii}`);
      }
      
      return {
        path: targetPath,
        offset,
        length: slice.length,
        total_size: buffer.length,
        hex_dump: lines.join('\n')
      };
    } catch (err) {
      return { error: err.message };
    }
  },

  find_files: async (args) => {
    const searchDir = resolve(args.directory);
    const results = [];
    const modifiedAfter = args.modified_after ? new Date(args.modified_after) : null;
    const pattern = args.pattern ? new RegExp(args.pattern.replace(/\*/g, '.*'), 'i') : null;
    
    const walkDir = (dir) => {
      try {
        const items = readdirSync(dir);
        for (const item of items) {
          const fullPath = join(dir, item);
          try {
            const st = statSync(fullPath);
            
            if (st.isDirectory()) {
              walkDir(fullPath);
            } else {
              let match = true;
              
              if (pattern && !pattern.test(item)) {
                match = false;
              }
              
              if (modifiedAfter && st.mtime < modifiedAfter) {
                match = false;
              }
              
              if (args.content && match) {
                try {
                  const content = readFileSync(fullPath, 'utf8');
                  if (!content.includes(args.content)) {
                    match = false;
                  }
                } catch {
                  match = false; // Can't read as text
                }
              }
              
              if (match) {
                results.push({
                  path: fullPath,
                  size: st.size,
                  modified: st.mtime.toISOString()
                });
              }
            }
          } catch (e) {
            // Skip inaccessible files
          }
        }
      } catch (e) {
        // Skip inaccessible directories
      }
    };
    
    walkDir(searchDir);
    return { directory: searchDir, count: results.length, results };
  },

  hash_file: async (args) => {
    const targetPath = resolve(args.path);
    
    if (!existsSync(targetPath)) {
      return { error: `File does not exist: ${targetPath}` };
    }
    
    try {
      const { createHash } = await import('crypto');
      const buffer = readFileSync(targetPath);
      
      return {
        path: targetPath,
        size: buffer.length,
        md5: createHash('md5').update(buffer).digest('hex'),
        sha1: createHash('sha1').update(buffer).digest('hex'),
        sha256: createHash('sha256').update(buffer).digest('hex')
      };
    } catch (err) {
      return { error: err.message };
    }
  }
};

// MCP message handling
function createResponse(id, result) {
  return {
    jsonrpc: JSONRPC_VERSION,
    id,
    result
  };
}

function createError(id, code, message) {
  return {
    jsonrpc: JSONRPC_VERSION,
    id,
    error: { code, message }
  };
}

async function handleMessage(msg) {
  const { id, method, params } = msg;
  
  switch (method) {
    case 'initialize':
      return createResponse(id, {
        protocolVersion: '2024-11-05',
        serverInfo: SERVER_INFO,
        capabilities: SERVER_INFO.capabilities
      });
    
    case 'initialized':
      return null; // No response needed
    
    case 'tools/list':
      return createResponse(id, {
        tools: Object.entries(TOOLS).map(([name, def]) => ({
          name,
          description: def.description,
          inputSchema: def.inputSchema
        }))
      });
    
    case 'tools/call':
      const toolName = params?.name;
      const toolArgs = params?.arguments || {};
      
      if (!toolHandlers[toolName]) {
        return createError(id, -32601, `Unknown tool: ${toolName}`);
      }
      
      try {
        const result = await toolHandlers[toolName](toolArgs);
        return createResponse(id, {
          content: [{
            type: 'text',
            text: typeof result === 'string' ? result : JSON.stringify(result, null, 2)
          }]
        });
      } catch (err) {
        return createError(id, -32000, err.message);
      }
    
    case 'ping':
      return createResponse(id, {});
    
    default:
      return createError(id, -32601, `Method not found: ${method}`);
  }
}

// Main server loop
async function main() {
  const rl = createInterface({
    input: process.stdin,
    output: process.stdout,
    terminal: false
  });
  
  process.stderr.write(`[mk2-bridge] V8 ${process.versions.v8} ready (Node ${process.version})\n`);
  
  for await (const line of rl) {
    if (!line.trim()) continue;
    
    try {
      const msg = JSON.parse(line);
      const response = await handleMessage(msg);
      
      if (response) {
        process.stdout.write(JSON.stringify(response) + '\n');
      }
    } catch (err) {
      process.stderr.write(`[mk2-bridge] Error: ${err.message}\n`);
      const errorResponse = createError(null, -32700, 'Parse error');
      process.stdout.write(JSON.stringify(errorResponse) + '\n');
    }
  }
}

main().catch(err => {
  process.stderr.write(`[mk2-bridge] Fatal: ${err.message}\n`);
  process.exit(1);
});
