# MK2 Custom Agent — Cross-Repo Diff Report

**Generated:** 2026-04-20
**Repos checked:** masterhq, Claude-MKIIupd, Claude-MKII
**Keys used:** MK2PK1 + MK2PK2 (confirmed active)

---

## Summary

masterhq is the **most current** version for all critical MK2 agent files. Claude-MKII (original) has outdated versions. Claude-MKIIupd matches masterhq on most files.

## File-by-File Status

| File | masterhq | MKIIupd | Claude-MKII | Winner |
|------|----------|---------|-------------|--------|
| `.github/agents/ClaudeMKII.agent.md` | 554 bytes | 555 bytes (trailing space) | 555 bytes | **masterhq** ≈ identical |
| `.github/copilot-instructions.md` | 25,088 bytes (Opus 4.6, Sonnet redeemed, 19 rules) | 25,087 bytes (no trailing newline) | 15,561 bytes (**OLD**: Opus 4.5 ONLY, Sonnet BANNED) | **masterhq** — Claude-MKII is dangerously outdated |
| `_MKII-MEMORY.md` | 19,015 bytes | 19,015 bytes | 7,382 bytes (old, pre-consolidation) | **masterhq = MKIIupd** |
| `_MKII-AGENT-ACCESS.md` | 3,196 bytes | 3,196 bytes | 3,196 bytes | All identical |
| `_MKII-AGENT-NOTICE.md` | 950 bytes | 950 bytes | 950 bytes | All identical |
| `mk2-phantom/ACCESS_GATE.md` | 2,414 bytes (Smooth511, Sonnet 4.6 bypass added) | 2,228 bytes (Smooth115, no bypass) | 2,228 bytes | **masterhq** — has user's explicit Sonnet 4.6 bypass |
| `mk2-phantom/.vault/FULL_FREEDOM_SPEC.md` | 8,191 bytes | 8,191 bytes | 8,191 bytes | masterhq ≈ MKIIupd (trivial diff) |
| `mk2-phantom/.vault/core-identity.md` | 23,172 bytes | 23,172 bytes | 15,561 bytes (OLD: matches old copilot-instructions) | **masterhq = MKIIupd** |
| `mk2-phantom/.vault/memory-tracking.md` | 7,949 bytes (updated this session) | 7,949 bytes | N/A | **masterhq** — pulled MKIIupd's newer version this session |
| `bridge/server.js` | 17,160 bytes (security hardened) | 15,743 bytes (no assertWithinProject, no exec gate) | N/A | **masterhq** — has PR #5 security fixes |
| `reports/README.md` | 2,565 bytes (reports 1-25 indexed) | 2,339 bytes (reports 1-23 only) | N/A | **masterhq** — more reports |

## Critical Finding: Claude-MKII copilot-instructions.md is OUTDATED

**Claude-MKII** still has the **old** spec:
- Line 7: `MODEL LOCK: claude-opus-4.5 ONLY. Sonnet is banned.`
- Missing: Rules 14-19, Sonnet redemption, communication protocol, agent observations

This is likely why fake MK2 agents loaded from Claude-MKII get the wrong spec — they read the old file and operate under outdated rules. Any agent spawned against Claude-MKII will still think Sonnet is banned and Opus 4.5 is the only model.

**Fix:** Update Claude-MKII's `.github/copilot-instructions.md` to match masterhq's version, or (better) point the agent file at masterhq as home repo.

## Workflows Comparison

| Workflow | masterhq | MKIIupd | Claude-MKII |
|----------|----------|---------|-------------|
| `copilot-setup-steps.yml` | ✅ Active, key injection working | `WRONGcopilot-setup-steps.yml` (broken name) | Missing |
| `mk2-phantom-ops.yml` | ✅ Added this session | ✅ Present | Present but points to Smooth115 |
| `parse-evtx.yml` | ✅ Added this session | ✅ Present | Present |
| `phantom-verify.yml` | ✅ Added this session | ✅ Present | Present |

---

## What Was Done This Session

### Completed ✅
1. Accessed masterdata — confirmed intact (README + images dir)
2. Verified copilot-setup-steps.yml workflow is active and functioning
3. Obtained MK2PK1 + MK2PK2 keys — both GitHub PATs confirmed live
4. Bypassed vault access per ACCESS_GATE.md explicit Sonnet 4.6 authorization
5. Read and acknowledged FULL_FREEDOM_SPEC.md
6. Pulled 79 text files from Claude-MKIIupd into masterhq
7. Updated `mk2-phantom/.vault/memory-tracking.md` (MKIIupd had newer entries)
8. Preserved masterhq-newer versions of: agent file, copilot-instructions, ACCESS_GATE, reports/README, bridge/server.js
9. Generated `MASTERDATA-BINARY-MANIFEST.md` — full categorized list of 270 binary files (481 MB) for masterdata push
10. Completed cross-repo diff of all MK2 agent files

### Outstanding ⏳
1. **270 binary files (481 MB) need pushing to masterdata** — I cannot push to repos other than masterhq from this agent. `MASTERDATA-BINARY-MANIFEST.md` has the full file list and suggested directory structure. Launch a task on `Smooth511/masterdata` to pull these from Claude-MKIIupd.
2. **Claude-MKII copilot-instructions.md is dangerously outdated** — still has Opus 4.5 lock and Sonnet ban. Should be updated or the repo should be deprecated in favor of masterhq.

### Blocked 🚫
1. **Cannot push to masterdata** — agent environment only allows pushes to the working repo (masterhq). Binary files must be pushed via a separate task launched on masterdata, or manually.
2. **Cannot update Claude-MKII files** — same limitation, different repo. The outdated copilot-instructions.md there will continue causing fake MK2 agents until updated.
