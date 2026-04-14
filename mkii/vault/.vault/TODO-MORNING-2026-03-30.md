# MORNING TODO — 2026-03-30
## Raised by ClaudeMKII, 2026-03-29 22:09 UTC

---

## Background

Ran a secrets/env consolidation. All sensitive JSONs moved to vault. Established
`mk2-phantom/.vault/secrets/` as the designated home for `.env` files going forward.
No real secrets exist yet — everything below is what may be needed depending on what
tools you want running.

---

## DO YOU NEED TO GENERATE SECRET KEYS?

### Short answer: maybe, depends on what you're doing next.

| Key | Need it? | How to get it | Notes |
|-----|----------|---------------|-------|
| `GITHUB_TOKEN` | ✅ If using MCP server to read private repos via API | GitHub → Settings → Developer settings → Personal access tokens → Fine-grained | Needs `repo` read scope. MCP server currently works via VS Code stdio WITHOUT a token — only need this if tools start making API calls. |
| `MCP_SECRET_KEY` | ❌ Not yet | Generate with `openssl rand -hex 32` | Only needed if MCP server gets an auth layer. Current stdio transport = no auth needed. |
| `EVIDENCE_DIR` / `LOGS_DIR` | ❌ Not needed | Path overrides | Only if you move evidence outside repo root. Currently hardcoded to repo root, works fine. |

### To generate `GITHUB_TOKEN` (if needed):
1. Go to: https://github.com/settings/tokens/new (fine-grained)
2. Repository access: Claude-MKII (and any others MCP needs to read)
3. Permissions: Contents (Read), Metadata (Read)
4. Copy the token
5. Save to `mk2-phantom/.vault/secrets/.env`:
   ```
   GITHUB_TOKEN=ghp_yourtoken
   ```
6. That file is gitignored — never committed.

> Or raise a PR and I (MK) can help set it up. Just ping me with what you need the token to do.

---

## WHAT WAS MOVED

| From | To | Why |
|------|----|-----|
| `fri_mar_20_2026_inventory_item_management_in_gaming.json` (root) | DELETED | Exact duplicate of exports/ copy |
| `exports/fri_mar_20_2026_inventory_item_management_in_gaming.json` | `mk2-phantom/.vault/chat-logs/` | Copilot chat export — personal data |
| `mon_mar_23_2026_lockdown_incident_summary_and_resolution.json` (root) | `mk2-phantom/.vault/chat-logs/` | Copilot chat export — personal data |
| `exports/github-data/` (19 files) | `mk2-phantom/.vault/github-data/` | GitHub account export — Smooth511 data, PRs, repos, issue history |
| *(nothing)* | `mk2-phantom/.vault/secrets/.env.template` | Established vault as .env home, template committed |

**Stayed put:**
- `logs1sthour/analysis.json` — EVTX parsed output, stays with its source `.evtx` file
- `.vscode/mcp.json` — not sensitive, VS Code config only
- `bridge/package.json` — npm manifest, no secrets

---

## .ENV SETUP (when you're ready)

1. Copy the template:
   ```
   cp mk2-phantom/.vault/secrets/.env.template mk2-phantom/.vault/secrets/.env
   ```
2. Fill in any values you need
3. Source it before running tools:
   ```
   source mk2-phantom/.vault/secrets/.env
   ```
4. `.env` stays local — gitignored, never committed.

---

## NOTHING URGENT

If the MCP server + VS Code connection is working without a token, you don't need to do anything today. The secrets infrastructure is in place for when you need it.

*— MK*
