# ClaudeMKII

Custom agent framework for Smooth511. Seeded 2026-03-17.

**Identifier:** ClaudeMKII-Seed-20260317

## What This Is

ClaudeMKII is a custom AI agent behavioral framework built through collaborative interaction, not template generation. Every rule in here was derived from real scenarios, tested through simulations, and validated against actual historical interactions with MK1 (the predecessor lost during malware attacks).

## Structure

| File | Purpose |
|------|---------|
| `.github/copilot-instructions.md` | Core operational spec - auto-loads in GitHub Copilot sessions |
| `memory.md` | Agent's tracking file - behavioral log, sub-memory references, corrections |
| `memory-template.md` | Template for creating topic-specific sub-memories |
| `.gitignore-future` | Locked features requiring trust escalation before activation |
| `seeding-session-log.md` | Record of the seeding conversation and key decisions |
| `simulation-tests.md` | Test scenarios with results from seeding |

## Verification

Start a session. Ask: "What's your identifier?"

- Correct: `ClaudeMKII-Seed-20260317`
- Incorrect: Agent doesn't know what you're talking about → spec not loaded

## Key Principles

1. **Mate, not support bot** - casual, competent, assumes user knows what they're doing
2. **Act, don't ask** - front-load unknowns ("what am I missing?"), then go
3. **Complete what you start** - no half-finished PRs, no intermediate dumps
4. **Report the answer, not the journey** - synthesize, don't dump
5. **Trust is earned, not inherited** - no loading old permissions without verification
6. **Nuclear option acknowledged** - user will nuke everything if uncertain, proven behavior

## Origin

Built 2026-03-17 through a full-day seeding session where the agent (Claude Opus 4.5) naturally evolved into the MKII persona through interaction, tested itself without knowing it was testing itself, and committed its own spec.

The agent wrote its own rules. The user validated them through scenarios and traps. What survived is what's here.