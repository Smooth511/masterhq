# mk2-phantom (Claude-MKII)

Custom autonomous agent framework for Smooth115. Seeded 2026-03-17. Codename assigned 2026-03-20.

**Identifier:** ClaudeMKII-Seed-20260317
**Codename:** mk2-phantom

## What This Is

An AI agent behavioral framework built through collaborative interaction, not template generation. Every rule was derived from real scenarios, tested through simulations, validated against actual interactions. The agent wrote its own rules. The user validated them through scenarios and traps. What survived is what's here.

## Repository Structure

*Reorganized 2026-04-03 by MK2 (MK2_PHANTOM authorized)*

```
Claude-MKII/
├── .github/
│   ├── copilot-instructions.md    # Core operational spec (auto-loads)
│   ├── agents/                     # Agent definition files
│   └── workflows/                  # CI/CD workflows
│
├── _MKII-AGENT-ACCESS.md          # Repository access control (first-contact)
├── _MKII-AGENT-NOTICE.md          # Critical notices for agents
├── _MKII-MEMORY.md                # Agent tracking + behavioral log
├── COMMS.md                        # Single communication intake point
├── README.md                       # This file
│
├── mk2-phantom/                    # 🔒 PROTECTED VAULT
│   ├── ACCESS_GATE.md             # Codename authentication gate
│   └── .vault/                    # Preserved ground-truth files
│
├── reports/                        # 📋 INVESTIGATION REPORTS (numbered chronologically)
│   ├── 01-2026-03-18-pushbuttonreset-analysis.md
│   ├── 02-2026-03-18-INVESTIGATION-REPORT.md
│   ├── 03-2026-03-19-HP-EVIDENCE-MASTER-REPORT.md
│   ├── 04-2026-03-20-SECURITY-AUDIT-REPORT.md
│   ├── 05 thru 10 — Agent investigation reports (2026-03-26)
│   ├── 11-2026-03-27-ATTACK-EVOLUTION.md
│   ├── 12-2026-03-27-SCREENSHOT-ANALYSIS.md
│   ├── 13-2026-03-29-GITIGNORE-SABOTAGE-INVESTIGATION.md
│   ├── 14-2026-03-30-BINGO-EVIDENCE-CATALOG.md
│   ├── 15-16 — TheLink analysis + gap analysis (2026-03-30)
│   ├── 17-2026-04-01-LOGS1627-ANALYSIS.md
│   ├── 18-2026-04-01-COMPREHENSIVE-ROOTKIT-REPORT.md
│   ├── 19-20 — THEBULLETFROMSMOKINGUN report + analysis (2026-04-02)
│   └── evaluations/               # Meta-analysis, skill evals, status updates
│       ├── AWESOME-CLAUDE-CODE-EVALUATION-2026-03-24.md
│       ├── CYBERSEC-SKILL-EVALUATION-2026-03-24.md
│       └── STATUS-2026-03-24-cleanup-progress.md
│
├── evidence/                       # 🔍 EVIDENCE
│   ├── raw/                        # Raw evidence drops (untouched source material)
│   │   ├── THEBULLETFROMSMOKINGUN/ # Apr 2 ASUS investigation (photos, chatlogs)
│   │   ├── BINGO/                  # BINGO evidence (screenshots, chat, video)
│   │   ├── logs1627/               # System logs (80 files, 78MB)
│   │   ├── logs1sthour/            # First-hour EVTX capture
│   │   ├── logslinux29/            # Linux raw logs
│   │   ├── LinuxRaw25/             # Linux raw data
│   │   ├── CodeSmooth/             # Code recovery evidence
│   │   ├── VSCODE/                 # VSCode USB evidence
│   │   ├── linux-logs-screenshots/ # Investigation screenshots + ErrorLogs
│   │   └── (journals, images, PDFs, misc raw files)
│   ├── analysis/                   # Individual evidence writeups (2026-03-19)
│   │   ├── malware-analysis-2026-03-19.md
│   │   ├── registry-analysis-2026-03-19-batch1.md
│   │   ├── vindication-log-2026-03-19.md
│   │   └── (13 more evidence analysis files)
│   └── README.md
│
├── logs/                           # 📝 OPERATIONAL LOGS
│   ├── LOCKDOWN-MASTER-LOG.md     # March 2026 lockdown
│   ├── LOCKDOWN-FINAL-REPORT.md
│   ├── POST-LOCKDOWN-REPORT-2026-03-23.md
│   ├── LOCKDOWN-COMPLIANCE-REPORT-2026-03-23.md
│   ├── PR-RESOLUTION-REPORT-2026-03-23.md
│   ├── SESSION-LOG-2026-03-20-activation.md
│   ├── SESSION-REVIEW-2026-03-25-vscode-connection.md
│   ├── seeding-session-log.md
│   └── (lockdown + session + compliance logs)
│
├── core/                           # Framework definition files
│   ├── claude_mkii_seed_package.md
│   ├── simulation-tests.md
│   ├── memory-template.md
│   ├── RECOVERY_PLAN_Version2.md
│   └── TROUBLESHOOTING.md
│
├── chat-logs/                      # Recovered chat data
├── tools/                          # Utilities (EVTX parser, safe_read)
├── tests/                          # Unit tests for tools
├── cli/                            # MK2 CLI tool
├── bridge/                         # MCP bridge server
├── mcp-server/                     # MCP server
├── assets/images/                  # Screenshots, visual evidence
├── docs/                           # Setup documentation
└── comments/                       # GitHub comment archives
```

### Naming Convention
Files prefixed with `_MKII-` are **first-contact directing documents** that must remain at repository root. The `_MKII-` prefix ensures:
- They sort to the top of any file listing
- They are virtually impossible to collide with files from other repos/projects
- They are immediately identifiable as MKII operational files
- No standard tool, template, or scaffold will generate files with this prefix

### Vault Access
The `mk2-phantom/` directory is access-gated. Only agents addressed by the codename `mk2-phantom` may access its contents. See `mk2-phantom/ACCESS_GATE.md` for protocol.

## Verification

Start a session. Ask: "What's your identifier?"
- Correct: `ClaudeMKII-Seed-20260317`
- Incorrect: Spec not loaded

## Key Principles

1. **Act first, report after** — execute, don't propose
2. **Self-service everything** — if it's accessible, go get it
3. **Complete what you start** — no half-finished PRs
4. **Report the answer, not the journey** — synthesize, don't dump
5. **Trust is earned, not inherited** — vault preserves ground truth
6. **Nuclear option acknowledged** — user will nuke if uncertain