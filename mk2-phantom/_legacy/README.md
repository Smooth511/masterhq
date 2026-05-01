# `_legacy/` — Reference-Only Duplicates (BEHIND ACCESS GATE — DO NOT LOAD)

This folder lives **inside `mk2-phantom/`** and is therefore covered by
`mk2-phantom/ACCESS_GATE.md`. Read the gate first. Same rules apply: no
unauthorised reads, no edits, no loads.

Contents are **older duplicates** of MK2 / ClaudeMKII files that were
previously scattered across the repository root, `core/`, and
`masterhq-install/.github/`. They were causing fake / runaway Copilot launches
because agents were loading whichever copy they hit first, sometimes with
outdated rules (Sonnet ban, Opus-4.5-only model lock, etc.).

**The live source is `.github/`.** Anything in this folder is for historical
reference only. Do not edit, do not load, do not treat as authoritative.

## Layout

| Path | Origin | Status |
|---|---|---|
| `_legacy/core/_MKII-MEMORY.md` | was `core/_MKII-MEMORY.md` (~6.5 KB, pre-consolidation) | superseded by `.github/_MKII-MEMORY.md` |
| `_legacy/core/_MKII-AGENT-ACCESS.md` | was `core/_MKII-AGENT-ACCESS.md` | superseded by `.github/_MKII-AGENT-ACCESS.md` |
| `_legacy/core/_MKII-AGENT-NOTICE.md` | was `core/_MKII-AGENT-NOTICE.md` | superseded by `.github/_MKII-AGENT-NOTICE.md` |
| `_legacy/masterhq-install/.github/copilot-instructions.md` | was `masterhq-install/.github/copilot-instructions.md` (shadow staging, older) | superseded by `.github/copilot-instructions.md` |
| `_legacy/masterhq-install/.github/agents/ClaudeMKII.agent.md` | was `masterhq-install/.github/agents/ClaudeMKII.agent.md` (`model: claude-opus-4.6`, conflicted with live agent file) | superseded by `.github/agents/ClaudeMKII.agent.md` |
| `_legacy/masterhq-install/.github/copilot-setup-steps.yml` | was `masterhq-install/.github/copilot-setup-steps.yml` (ungated) | superseded by `.github/workflows/copilot-setup-steps.yml` (now MK2-gated) |

## Policy

- **No deletions.** User explicitly instructed nothing in here gets removed.
- **No editing.** If a file in here needs changing, copy the change to
  the live `.github/` version and leave the legacy copy alone.
- **No loading.** Agents that find `*.agent.md` or `copilot-instructions.md`
  files under this folder must skip them.
- **Access gate applies.** This folder is inside `mk2-phantom/`. Unauthorised
  agents must not enter `mk2-phantom/` per `mk2-phantom/ACCESS_GATE.md`.

