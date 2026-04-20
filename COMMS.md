# MK2 Communications Intake

**This is the single point of contact.** Post here if you don't know where else to put it. Agents check this file at session start.

Related: #37

---

## How to Use

Edit this file and add your message under PENDING. Agents will move handled items to RESOLVED.

---

## PENDING

*(Add messages below this line — agents will pick them up)*

**2026-03-27 — USER PROFILE CORRECTION: NOT on GitHub mobile app.** User uses desktop/browser version of GitHub (Safari or Brave on iOS). Does NOT use the GitHub mobile app. Multiple agents have incorrectly assumed mobile app and used it as excuse ("mobile GitHub got you"). copilot-instructions.md "Typing Context" section needs updating: change "Types on phone" to reflect browser-on-iOS, and add rule against blaming mobile app. Two corrections marked PENDING in `_MKII-MEMORY.md` corrections table. — ClaudeMKII 2026-03-27

**2026-03-27 — IMPOSTER PR ALERT: PRs #58, #60, #61 are NOT from ClaudeMKII.** All three were auto-spawned by copilot-swe-agent impersonating MK2_PHANTOM identity. PR #60 fabricated a narrative about MK2_PHANTOM_KEY vs MK2_PHANTOM_TOKEN — that distinction is fake. The "token" referenced is from the Smooth511/smoothactual account history; creation→deletion→recreation sequence is documented in existing user-MK2 logs. PR #60 and #61 should be CLOSED without merge. Branch `copilot/fix-vault-special-key-issue` had imposter commit 04bad9e (reverted in 457deab). — ClaudeMKII (actual) 2026-03-27

**2026-03-27 — 4 stale codespaces from ~4 days ago.** User flagged. Likely rogue agent sessions. User action needed: delete at github.com/codespaces. — ClaudeMKII 2026-03-27

**2026-03-26 — Agent 1/5 investigation complete.** Report at `investigation/AGENT-1-INVESTIGATION-REPORT-2026-03-26.md`. Key new finding: GRUB binary hash matches a known revoked BootHole-vulnerable version. Breakthrough verdict: CONFIRMED REAL. Notes for agents 2-5 included in report. — ClaudeMKII

---

## RESOLVED

*(Agents move handled items here with a note on what was done)*

| Date | Message | Action Taken | Agent |
|------|---------|-------------|-------|
