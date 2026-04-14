# mk2-phantom (Claude-MKII)

Custom autonomous agent framework for Smooth511. Seeded 2026-03-17. Codename assigned 2026-03-20.

**Identifier:** ClaudeMKII-Seed-20260317
**Codename:** mk2-phantom

## What This Is

An AI agent behavioral framework built through collaborative interaction, not template generation. Every rule was derived from real scenarios, tested through simulations, validated against actual interactions. The agent wrote its own rules. The user validated them through scenarios and traps. What survived is what's here.

## Repository Structure

```
Claude-MKII/
├── .github/
│   ├── copilot-instructions.md    # Core operational spec (auto-loads)
│   ├── agents/                     # Agent definition files
│   └── workflows/
│       ├── parse-evtx.yml         # EVTX log parser
│       ├── phantom-verify.yml     # Token verification + permissions check
│       └── mk2-phantom-ops.yml    # Cross-repo operations dispatch
├── _MKII-AGENT-ACCESS.md          # Repository access control (first-contact)
├── _MKII-AGENT-NOTICE.md          # Critical notices for agents
├── _MKII-MEMORY.md                # Agent tracking + behavioral log
├── README.md                       # This file
├── mk2-phantom/                    # 🔒 PROTECTED VAULT
│   ├── ACCESS_GATE.md             # Codename authentication gate
│   └── .vault/                    # Preserved ground-truth files
├── core/                           # Framework definition files
│   ├── seeding-session-log.md     # Seeding process record
│   ├── simulation-tests.md        # Test scenarios + results
│   ├── memory-template.md         # Sub-memory template
│   └── .gitignore-future          # Locked future features
├── evidence/                       # Investigation evidence
├── investigation/                  # Analysis reports
├── chat-logs/                      # Recovered chat data
├── logs/                           # Operational logs
├── logs1sthour/                    # First-hour EVTX capture
├── tools/                          # Utilities (EVTX parser, etc.)
├── assets/images/                  # Screenshots, visual evidence
└── exports/github-data/            # GitHub data export JSONs
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