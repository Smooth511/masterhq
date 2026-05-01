# masterhq

Consolidated investigation HQ — all text content, reports, evidence analysis, and operational files from the MK2 investigation framework across 15 repositories and 2 GitHub accounts.

## Structure

| Directory | Files | Contents |
|-----------|-------|----------|
| `reports/` | 24 | Numbered investigation reports (02–24) |
| `evidence/` | 80+ | Analysis docs, raw text evidence (BINGO, TBFSG, OCR, Linux logs) |
| `investigations/` | 15+ | DATABASE investigation files |
| `ios-investigation/` | 300+ | iOS logs, forensic analysis from Threat-2 |
| `windows-investigation/` | 20+ | Windows EVTX analysis, malware reports |
| `docs/` | 20+ | Guides, context docs, chat reports |
| `core/` | reference | Older MK2 identity files — superseded by `.github/` (do not load). Live MK2 docs are in `.github/`. |
| `_legacy/` | reference | Reorganised duplicates from prior layout. Read-only, do not load. See `_legacy/README.md`. |
| `mk2-phantom/.vault/` | 10+ | Vault text content |
| `logs/` | 15+ | Operational logs, lockdown reports |
| `chat-logs/` | 5+ | Transcripts and exports |
| `tools/` | 5+ | CLI scripts |
| `bridge/` | 5+ | Bridge server |
| `archive/` | 50+ | Source repo archives, pulls, exports |

**Binary evidence** (images, videos, journals, EVTX) → [masterdata](https://github.com/Smooth511/masterdata)

## Reports Index

| # | Date | Title |
|---|------|-------|
| 02 | 2026-03-18 | Investigation Report |
| 04 | 2026-03-20 | Security Audit Report |
| 05 | 2026-03-26 | Agent 1 Investigation Report |
| 06 | 2026-03-26 | Agent 5 Investigation Report |
| 07 | 2026-03-26 | Linux Agent 1 Investigation Report |
| 08 | 2026-03-26 | 5-Agent Review Report |
| 09 | 2026-03-26 | UEFI/MOK/Kernel Evidence |
| 10 | 2026-03-26 | MK2 Log Analysis Report |
| 11 | 2026-03-27 | Attack Evolution |
| 12 | 2026-03-27 | Screenshot Analysis |
| 13 | 2026-03-29 | Gitignore Sabotage Investigation |
| 14 | 2026-03-30 | BINGO Evidence Catalog |
| 15 | 2026-03-30 | THELINK Comprehensive Analysis |
| 16 | 2026-03-30 | THELINK Gap Analysis |
| 17 | 2026-04-01 | LOGS1627 Analysis |
| 18 | 2026-04-01 | Comprehensive Rootkit Report |
| 19 | 2026-04-02 | THEBULLETFROMSMOKINGUN Report |
| 20 | 2026-04-02 | THEBULLETFROMSMOKINGUN Analysis |
| 21 | 2026-04-11 | AICHAT + OCR220SS Analysis |
| 22 | 2026-04-11 | Pre-Overlay Breach: Initramfs & Ventoy Boot Chain |
| 23 | 2026-04-14 | Cross-Repo Verification Report |
| 24 | 2026-04-14 | Recovery Mode Root Shell Tactical Command Analysis |

## Source Repos Consolidated

| Repository | Account | Role | Status |
|-----------|---------|------|--------|
| Claude-MKIIupd | Smooth511 | Primary source (most complete) | ✅ Consolidated |
| Claude-MKII | Smooth115 | Home base / fork parent | ✅ Consolidated |
| Claude-MKII | Smooth511 | Original creation + HP evidence | ✅ Consolidated |
| DATABASE | Smooth511 | Investigation data + HOTDROP | ✅ Consolidated |
| DATABASE | Smooth115 | Mirror | ✅ Deduped |
| AgentHQ | Smooth511 | Agent config (1 file) | ✅ Consolidated |
| Threat-2-the-shadow-dismantled- | Smooth511 | iOS investigation (381 files) | ✅ Consolidated |
| malware-invasion.-battle-of-the-rootkits | Smooth511 | Windows EVTX + malware reports | ✅ Consolidated |
| Smashers-HQ | Smooth511 | Early investigation HQ | ✅ Consolidated |
| Issue-3 | Smooth115 | Issue tracker | ✅ Consolidated |
| MKIIVAULT | Smooth115 | Vault placeholder | ✅ Consolidated |
| smooth115_database | Smooth511 | Mirror of DATABASE | ✅ Deduped |
| Smooth115_Issue-3 | Smooth511 | Mirror | ✅ Deduped |

**603 unique text files** consolidated, **458 duplicates** removed, **0 errors**.

## MK2 Agent Status

| Component | Status |
|-----------|--------|
| `copilot-setup-steps.yml` | ✅ `.github/workflows/` (correct location) |
| `copilot-instructions.md` | ✅ Full MKII spec loaded |
| `ClaudeMKII.agent.md` | ✅ Opus 4.6, custom agent |
| `MK2PK1` secret (Smooth511) | ✅ Set in repo |
| `MK2PK2` secret (Smooth115) | ✅ Set in repo |

## How Keys Work

On agent launch, the `copilot-setup-steps.yml` workflow injects repo secrets as environment variables:
- `$MK2PK1` → Smooth511 full access
- `$MK2PK2` → Smooth115 full access

The agent can then use these to access private repos across both accounts.
