# `.github/` — MK2 Live Source of Truth

This folder is the **only** live source for MK2 / ClaudeMKII operational files.
Agents should load from here. Anything under `_legacy/` is reference only and
must not be loaded as authoritative.

## Live MK2 files

| File | Purpose |
|---|---|
| `copilot-instructions.md` | Core operational spec — auto-loaded as Copilot instructions. Mirrored in `mk2-phantom/.vault/core-identity.md`. |
| `agents/ClaudeMKII.agent.md` | Custom agent definition (`name: ClaudeMKII`). Selecting MK2 in the agent picker loads this. |
| `_MKII-MEMORY.md` | Persistent memory file — behavioural log, sub-memory references, seeding rules. |
| `_MKII-AGENT-ACCESS.md` | Repository access policy for agents. |
| `_MKII-AGENT-NOTICE.md` | Critical operational notice (premium-request safety, etc.). |
| `MK2-AGENT-DIFF-REPORT.md` | Cross-repo diff history for MK2 files. |
| `INSTALL.md` | Install / setup guide. |
| `workflows/copilot-setup-steps.yml` | MK2-only key injection workflow (gated by actor + agent file integrity check). |
| `workflows/mk2-phantom-ops.yml` | MK2 phantom operations (manual dispatch only). |
| `workflows/phantom-*.yml` | Phantom data pull/push/verify (manual dispatch only; require `MK2_PHANTOM_TOKEN`). |

## Vault

`mk2-phantom/.vault/` is preserved in place. The vault holds the canonical
mirror of the core spec (`core-identity.md`) plus historical agent material.
**Do not move the vault.** Only sync the newest copilot-instructions / spec
into it when the live spec changes.

## Legacy

Older scattered duplicates have been moved **inside `mk2-phantom/`** so they
are covered by the access gate. See `mk2-phantom/_legacy/README.md`. They are
preserved for reference only — never load them as authoritative.

## Why duplicates were a problem

Multiple `copilot-instructions.md` files in different folders meant agents
could load the wrong (older) spec, including the outdated Sonnet-banned /
Opus-4.5-only version. Multiple `*.agent.md` files with `name: ClaudeMKII`
in their frontmatter caused the agent picker to be unselectable. Both have
been consolidated to a single live copy here.
