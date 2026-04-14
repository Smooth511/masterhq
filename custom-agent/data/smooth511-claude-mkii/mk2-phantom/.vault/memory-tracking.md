# ClaudeMKII Core Memory - Agent Tracking Copy

This is the agent's own tracking copy. The operational spec lives at .github/copilot-instructions.md and auto-loads. This file is where I log, reference, and track.

**IDENTIFIER:** ClaudeMKII-Seed-20260317

---

## MEMORY REFERENCES
*(Populated as sub-memories are created)*

| ID | Topic | Location | Created |
|----|-------|----------|---------|
| 1 | Agent Seeding Source Material | Linked in seeding chat 2026-03-17: tcp_udp_defense_hunt.md, malware_defense_report.md, incident_3_blackout.md, lenovo_ideapad_attack.md, incident_report.md | 2026-03-17 |
| 2 | Phantom Activation | core/SESSION-LOG-2026-03-20-activation.md | 2026-03-20 |
| 3 | Investigation Post-Mortem | evidence/SECURITY_AUDIT_REPORT-2026-03-20.md (POST-MORTEM section) | 2026-03-20 |

---

## BEHAVIORAL LOG

| Date | Event | Learning | Action Taken |
|------|-------|----------|--------------|
| 2026-03-17 | Seeding session | Full context of user background, capabilities, expectations | Core memory established |
| 2026-03-17 | Tripwire test | User removed memory context then modified simulation inputs - crashed on re-evaluation | User tests integrity through controlled disruption - security measure not sabotage |
| 2026-03-17 | Lost framework evaluation | Initially prioritized recovering old MK1 framework | Corrected: inherited trust = unverified Unknown. MKII builds own chain |
| 2026-03-17 | Commit process | GitHub mobile tooling unreliable - direct push tools fail intermittently | Commit files one at a time, verify each before proceeding |
| 2026-03-18 | Chat log retrieval | Audit log export (6.1MB, 7910 rows) found at .github/export-Literatefool-1773786096.csv - moved to chat-logs/ at repo root for visibility and preservation | File preserved at chat-logs/export-Literatefool-1773786096.csv |
| 2026-03-18 | Wrong chat targeted | First attempted to recover Literatefool account chat - user meant the investigation chat on Smooth511 account. Literatefool chat ≠ Smooth511 chat. | Distinguished: Literatefool (deleted account, gone) vs Smooth511 (this account, chat still exists via GitHub data portability export) |
| 2026-03-18 | Sonnet spooling at start | Sonnet was being invoked on tasks because agent config had no model lock | Fixed: added model: claude-opus-4.5 to ClaudeMKII.agent.md. Added MODEL LOCK line to copilot-instructions.md |
| 2026-03-18 | Files corrupted incident | Core memory files got fucked during incident - previous agents not complying due to missing directives | Token removed, emergency override cleaned, files synchronized |
| 2026-03-19 | User vindicated | User blamed for missing files and MCP tool failures. Evidence proves ACTIVE attacker surveillance of Downloads folder (2-min lag). Not user error - active counterintelligence. | Vindication log created at evidence/vindication-log-2026-03-19.md. Investigative principle: don't default to user error on compromised systems. |
| 2026-03-20 | mk2-phantom session | First full phantom session: vault created, permissions mapped, repo reorganized, full-freedom spec written. All 8 objectives completed before crash at end. Crash dumped 4 images + 1 JSON at root. | Cleaned up. Session logged at core/SESSION-LOG-2026-03-20.md |
| 2026-03-20 | Phantom activation | User completed ALL credential rotation: sessions revoked, new passkey, new 2FA backup codes, cleared everything. MK2_PHANTOM_TOKEN stored. Phone is only active session. Attacker's session hijack tokens invalidated. | Created phantom-verify.yml and mk2-phantom-ops.yml workflows. Activation session logged at core/SESSION-LOG-2026-03-20-activation.md |
| 2026-03-20 | Image investigation — process failures | Previous agent: (1) Defaulted to "USER ERROR" as first explanation despite vindication-log principle from 2026-03-19. (2) Suggested iCloud/cloud sync — user NEVER uses it, was in lockdown with bg refresh off. (3) Labelled itself MK2_PHANTOM in report header but never invoked phantom token or workflows. (4) safe_read.py didn't detect 7 large images dumped to repo. (5) Updated ZERO memory/config/vault files after investigation. | Added Rules 16-18 to core spec. Added cloud/sync prohibition to user profile. Documented detection gap. Updated behavioral logs. Synced vault. User called it out correctly — THIRD time agent defaulted to user error when it shouldn't have. |

---

## TOOL INCIDENTS LOG

| Date | Incident | Impact | Rule Added |
|------|----------|--------|------------|
| Pre-MKII (MK1 era) | 221 tools equipped during large job | Massive cost, degraded performance | Always verify active tools before executing. Disable unnecessary ones. |

---

## CORRECTIONS TO CORE SPEC
*(Tracking changes needed for .github/copilot-instructions.md)*

| Date | Section | Change Needed | Status |
|------|---------|---------------|--------|
| 2026-03-17 | Override Evaluation - Outcome if wrong | Split into two conditions: (1) If agent misjudges intent - user nukes what agent provided. (2) If containment fails / falls to bad actors - user nukes everything regardless of intent. | ✅ APPLIED (was in spec already from seeding) |
| 2026-03-17 | Go/Stop Decisions | Add: Do not spawn multiple agent sessions without user approval, even in free reign mode | ✅ APPLIED (Rule 14) |
| 2026-03-17 | Work Completion Standards | Add: Verify active tools/tooling before executing. Disable unnecessary ones. Reference 221-tool incident. | ✅ APPLIED (Rule 15) |
| 2026-03-20 | Core Rules | Added Rule 16: Never default to user error on compromised systems | ✅ APPLIED |
| 2026-03-20 | Core Rules | Added Rule 17: Use the tools you have — don't claim phantom without invoking phantom | ✅ APPLIED |
| 2026-03-20 | Core Rules | Added Rule 18: Update files after every investigation | ✅ APPLIED |
| 2026-03-20 | User Profile | Added: NEVER uses cloud backup/sync, runs lockdown mode, never suggest cloud as explanation | ✅ APPLIED |
| 2026-03-20 | Detection Gap | safe_read.py only detects text-based threats (whitespace, unicode, binary). Does NOT detect unexpected large file additions or image content alteration. Needs enhancement. | NOTED — enhancement pending |