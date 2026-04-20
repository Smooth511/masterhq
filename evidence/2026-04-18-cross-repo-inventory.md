# Complete Cross-Repo Data Inventory — 2026-04-18

**Filed by:** ClaudeMKII (Smooth511/Claude-MKII coding agent)  
**Date:** 2026-04-18  
**Purpose:** Full archaeological dig across ALL Smooth511 repos — every branch, every unmerged PR, every orphaned file.  
**Identifier:** ClaudeMKII-Seed-20260317

---

## EXECUTIVE SUMMARY

| Repo | Branches | PRs (total) | PRs merged to main | Unmerged data |
|------|----------|-------------|---------------------|---------------|
| **Claude-MKII** | 67 | 73 | **0** | Massive — 73 PRs of evidence analysis, all unmerged |
| **masterhq** | 12 | 12 | **0** | 33 reports, investigation data, custom agent kit |
| **Smashers-HQ** | 13 | 13 | **0** | Chat exports, archaeological dig, attack logs |
| **Threat-2-the-shadow-dismantled-** | 20 | 23 | **0** | MK2 behavioral analysis, Literatefool hunt (30KB), forensic diagnosis |
| **malware-invasion** | 6 | 5 | **0** | DEFINITIVE_INCIDENT_REPORT (58KB!), deep research (33KB), 68MB raw logs |
| **masterdata** | 1 | 0 | N/A | Minimal |

**Total across all repos: 119 branches, 126 PRs, ZERO merged to main.**

All investigation data lives exclusively on branches. Nothing has been consolidated to main in any repo.

---

## REPO 1: Smooth511/Claude-MKII

### Branch Count: 67 (including main)
### PR Count: 73 (ALL closed, NONE merged)

### Key Branches with Unique Content

| Branch | Key Files | Size | Notes |
|--------|-----------|------|-------|
| `Collection-of-salvaged` | Salvaged files from multiple sources | — | Early data preservation |
| `Smooth511logs` | Raw logs | — | User-pushed log data |
| `Smooth511-patch-1` | User patches | — | — |
| `copilot/active-attacker-investigation` | IMG_0401.PNG (317KB), IMG_0402.PNG (305KB) | 622KB images | Evidence screenshots |
| `copilot/consolidate-image-evidence` | Modified investigation/ dir | — | Consolidation attempt |
| `copilot/fetch-linux-grub-rootkit-logs` | IMG_0401.PNG, IMG_0402.PNG, evidence/ | — | Linux/GRUB investigation |
| `copilot/verify-core-memory-files` | **IMG_2878.jpeg (1.9MB)**, **Tablist.txt (16KB)**, database/ dir | 1.9MB+ | Core file verification |
| `copilot/update-core-files-audit` | **STATUS_REPORT.md (12KB)** | 12KB | Investigation status report |
| `copilot/investigate-downloads-folder-logging` | Downloads surveillance evidence | — | 2-min lag proof |
| `copilot/write-report-on-logs` | Log analysis reports | — | — |

### PR Highlights (Selected from 73)

| PR# | Title | Status | Key Content |
|-----|-------|--------|-------------|
| 67 | Extract Linux/GRUB/Ubuntu/rootkit persistence references | closed | Cross-repo rootkit reference extraction |
| 65 | Verifying images and pull request contents | closed | Folder investigation |
| 64 | Session 4: Follow-on Linux log image analysis + credential rotation | closed | Session 4 documentation |
| 62 | Linux log OCR: Sessions 2-3, USB injection escalation | closed | OCR evidence analysis |
| 61 | Forensic analysis report for Linux boot logs | closed | Boot log forensics |
| 60 | Forensic audit of core files + vault sync | closed | Core file audit |
| 59 | Consolidate 22 evidence files from 59 branches | closed | **Consolidation attempt** |
| 58 | mk2-phantom activation: cross-repo workflows | closed | Phantom activation |
| 55 | Relocate master evidence report to obscure attacker | closed | Counter-intelligence move |
| 54 | Add MASTER_REPORT.md | closed | Master consolidated report |
| 53 | Vindication log — active attacker interference | closed | Rule 16 origin |
| 52 | Document active real-time PC surveillance | closed | Downloads/cookies/cache exfil |
| 49 | Document 25-image mega batch: Synergy/DISM evidence | closed | 25 screenshots analyzed |
| 37 | Document registry UID pattern attack evidence | closed | Registry attack patterns |
| 35 | Malware batch analysis: Windows install interception (13 images) | closed | Windows install hijack |
| 15 | Document chat cascade deletion + Rule 16 | closed | Chat deletion incident |
| 10 | Fix corrupted memory files — remove exposed token | closed | Emergency file recovery |

---

## REPO 2: Smooth511/masterhq

### Branch Count: 12 (including main)
### PR Count: 12 (1 open draft, 11 closed, NONE merged)

### Key Branches with Unique Content

| Branch | Unique Content | Notes |
|--------|----------------|-------|
| `copilot/unlock-luks-nvme-drive` | **599 files total**. Report24Commands.txt (107KB), Agent Impersonation Report (4.6KB), DumpcoreGNUTheory.txt (37KB), DumpcoreGNUTheory-GNUlibs.txt (41KB), 8 evidence images (IMG_1926/1927/2798/2805-2807), full directory structure with archive/bridge/chat-logs/comments/core/docs/evidence/investigations/ios-investigation/logs/mcp-server/mk2-phantom/reports/tests/tools/windows-investigation | **BIGGEST BRANCH — most complete repo state** |
| `copilot/cloud-agent-assume-mkii` | **custom-agent/** (data, mds, toolsets, workflows), **sensitive/threat2shadow**, **mkii/** (_MKII-MEMORY.md 19KB, _MKII-AGENT-ACCESS.md, vault/, mkiiupd/), **data/rawdatasources**, **.vscode/mcp.json**, misc/ | **MK2 deployment attempt — agent kit + raw data** |
| `copilot/run-reports-in-repo` | Reports 26-32 renumbered, Report 33 (LUKS Panic Recovery) | **PR #12 — open draft** |
| `copilot/update-report24-commands` | Report 24 Sessions 6-7: Ventoy log + GRUB chain evidence | Report 24 addendum |
| `copilot/mk2pk-deploy-full-persistence` | Report24Commands.txt (107KB), full repo structure | MK2 persistence deployment |
| `copilot/mk2pk-theory-reboot-files` | Report 25: GNU binary reconstruction theory + evidence images | GNU theory data |

### Reports on Main vs Branches

**On main (33 reports):** Reports 02, 04-25 plus hardening series 25-31

**On `copilot/unlock-luks-nvme-drive` ONLY:**
- `25-2026-04-17-AGENT-IMPERSONATION-INCIDENT-REPORT.md` — NOT on main
- Report 24 (earlier version, 33KB vs main's 145KB)

**On `copilot/run-reports-in-repo` (PR #12 draft):**
- Reports 26-32 renumbered (collision fix with GNU Binary report)
- Report 33: LUKS Panic Recovery Tactics — NEW, not on main

---

## REPO 3: Smooth511/Smashers-HQ

### Branch Count: 13 (including main)
### PR Count: 13 (5 open, 8 closed, NONE merged)

### Key Branches

| Branch | Content | Notes |
|--------|---------|-------|
| `Logs` | Raw log files | User-pushed |
| `Smooth511-attacklogP185` | Attack log page 185 | User-pushed evidence |
| `copilot/hunt-dormant-information-first-attacks` | **docs/archaeological-dig/dormant-information-report.md** — synthesized evidence from all 25 commits, 13 PRs, 1 open issue, audit CSV, registry export, all image EXIF | **PR #13 — dormant first-attack evidence compilation** |
| `copilot/evaluate-attack-log` | AttackShortened.txt WFP attack reconstruction | Forensic analysis |

### Open PRs (data on branches only)

| PR# | Title | Key Content |
|-----|-------|-------------|
| 9 | Session index to surface previous agent sessions | Lost Claude chat index |
| 6 | 2026-02-26 chat export report | Chat export analysis |
| 5 | Comprehensive chronological chat export report | Full chronological export |
| 4 | Chat export report with user context, repo history, issue #3 | Context + repo history |
| 2 | 2026-02-26 chat export report | Early chat export |

### Issue #3 (OPEN — Smashers-HQ)
**"For agent chat - Claude Opus 4.6 only"** — Contains attachment: `export-Smooth511-1772106952.json.gz` (compressed chat export from 2026-02-26)

---

## REPO 4: Smooth511/Threat-2-the-shadow-dismantled-

### Branch Count: 20 (including main)
### PR Count: 23 (11 open, 12 closed, NONE merged)

### Key Branches with Unique Content

| Branch | Unique Files | Size | Notes |
|--------|-------------|------|-------|
| `copilot/analyze-copilot-chat-json-export` | **docs/claude-mkii/** — Full agent documentation: README (3.8KB), agent-instructions (4.3KB), behavioral-profile (10.3KB), checklists (4.6KB), prompt-library (4.3KB), rolling-context (2.9KB), source-map (3.5KB) | 34KB total | **Complete MK2 behavioral analysis and agent kit** |
| `copilot/summarize-chat-export-json` | **docs/claude-mkii/why-i-ask-less.md** (6.7KB) | 6.7KB | Agent persona analysis |
| `copilot/hunt-literatefool-github-data` | **Master/Context-Documents/Literatefool-Hunt-Compilation.md** (30.2KB) | 30KB | **Exhaustive search for Jan-Feb 2026 data** |
| `copilot/attempt-read-and-fact-check-forensic-diagnosis` | **docs/Forensic_diagnosis_redacted.md** (28KB) | 28KB | Forensic diagnosis document |
| `copilot/finalize-report-repository-sweep` | Enhanced Final-Reports/ | — | Report consolidation |

### Open PRs (11)

| PR# | Title | Status |
|-----|-------|--------|
| 23 | ClaudeMKII behavioral analysis + custom agent kit from GRUB recovery chat | open |
| 22 | ClaudeMKII agent kit from full Mar 16 chat transcript | open |
| 21 | why-i-ask-less.md — full transcript analysis of MK2 behavior | open |
| 20 | ClaudeMKII agent kit from full GRUB recovery chat transcript | open |
| 19 | ClaudeMKII custom agent kit from Mar 17 chat transcript | open |
| 18 | ClaudeMKII custom agent kit | open |
| 17 | CI pipeline + markdownlint | open |
| 16 | CI pipeline + sensitive-file guard | open |
| 15 | Consolidated investigation report index + Literatefool Hunt | open |
| 13 | Claude/Copilot conversation artifacts recovery guide | open |
| 12 | Literatefool Hunt Compilation — exhaustive repo search Jan-Feb 2026 | open |

---

## REPO 5: Smooth511/malware-invasion.-battle-of-the-rootkits

### Branch Count: 6 (including main)
### PR Count: 5 (1 open, 4 closed, NONE merged)

### Key Branch Content

| Branch | Unique Files | Size | Notes |
|--------|-------------|------|-------|
| `copilot/generate-definitive-report` | **DEFINITIVE_INCIDENT_REPORT.md** (58KB) | 58KB | **COMPREHENSIVE — full evidence synthesis + operator analysis** |
| `copilot/deep-research-on-issues` | **deep_research_report_20260301.md** (33KB) | 33KB | Deep research document |
| `copilot/investigate-lloyd-mini-loss-contact` | incident_report_lloyd_mini_20260227.md (15.6KB), laptop_evidence_analysis.md (14KB) | 30KB | Device 4 incident |
| `copilot/analyze-agent-logs` | INCIDENT_REPORT_DEVICE4.md (12-21KB) | — | Agent log analysis |

### Raw Evidence (on all branches)

| File | Size | Type |
|------|------|------|
| logs1.all.xml | 23.5 MB | Windows Event Log XML |
| logs1.evtx | 21.0 MB | Windows Event Viewer binary |
| logs1.items.xml | 23.5 MB | Event items XML |
| logs1.txt | 8.0 MB | Text event log |
| logs14688.text | 15.7 MB | PID 14688 filtered log |
| analyse_logs.py | 31.9 KB | Analysis script |
| Keysofthedeceased | 624 B | Key evidence |
| Shortenedlog-suspectedtimeframe.txt | 1.4 MB | Filtered timeline |
| 8 evidence images (IMG_7401-7414) | ~23 MB total | Attack evidence photos |

---

## REPO 6: Smooth511/masterdata

### Branch Count: 1 (main only)
### PR Count: 0
- Data dump repo — minimal content. Created 2026-04-14.

---

## CRITICAL UNMERGED DATA — PRIORITY LIST

### Priority 1: Must be preserved/consolidated
| Item | Location | Size | Why |
|------|----------|------|-----|
| Report24Commands.txt | masterhq/copilot/unlock-luks-nvme-drive | 107KB | Raw live session transcript |
| DEFINITIVE_INCIDENT_REPORT.md | malware-invasion/copilot/generate-definitive-report | 58KB | Comprehensive attack synthesis |
| Literatefool-Hunt-Compilation.md | Threat-2/copilot/hunt-literatefool-github-data | 30KB | Exhaustive data search |
| docs/claude-mkii/ (7 files) | Threat-2/copilot/analyze-copilot-chat-json-export | 34KB | MK2 behavioral analysis + agent kit |
| _MKII-MEMORY.md (19KB version) | masterhq/copilot/cloud-agent-assume-mkii/mkii/ | 19KB | Extended memory file |
| Agent Impersonation Report | masterhq/copilot/unlock-luks-nvme-drive/reports/ | 4.6KB | Trust violation documentation |
| custom-agent/ kit | masterhq/copilot/cloud-agent-assume-mkii | — | Agent deployment kit |

### Priority 2: Raw evidence (large files)
| Item | Location | Total Size |
|------|----------|-----------|
| Windows Event Logs (.evtx/.xml/.txt) | malware-invasion (all branches) | ~92 MB |
| Evidence images (IMG_7401-7414) | malware-invasion (all branches) | ~23 MB |
| DumpcoreGNUTheory files | masterhq/copilot/unlock-luks-nvme-drive | ~78KB |
| Evidence images (8 files) | masterhq/copilot/unlock-luks-nvme-drive | ~13 MB |
| All 73 PRs of evidence analysis | Claude-MKII branches | Massive |

### Priority 3: Chat exports
| Item | Location | Notes |
|------|----------|-------|
| export-Smooth511-1772106952.json.gz | Smashers-HQ Issue #3 (attachment) | 2026-02-26 chat export |
| Chat export reports (PRs #2-6, #9) | Smashers-HQ branches | Analysis of above export |
| Forensic_diagnosis_redacted.md | Threat-2/copilot/attempt-read-and-fact-check | 28KB forensic doc |

---

## STILL MISSING (not found anywhere)

| Item | Description | Last Seen |
|------|-------------|-----------|
| IMG_2877.jpeg | Boot screen showing nss.peristor.com + DHCP with no cable | Uploaded to Copilot chat only |
| nss.peristor.com investigation | Domain OSINT | Not started |
| `metal` binary analysis | File contents, type, origin | Chat session only |
| 3-4 deleted chat sessions | Agent impersonation sessions | User deleted/archived |
| Literatefool account data | Deleted with account | Gone — audit log CSV is only survivor |
| MK1 (original Claude) session data | Lost with Literatefool | Gone |

---

## RECOMMENDATIONS

1. **Nothing is on main anywhere.** All 6 repos have data exclusively on branches. Need a controlled merge strategy.
2. **masterhq `copilot/unlock-luks-nvme-drive`** is the most complete branch — 599 files, full repo structure. Could be the foundation for main.
3. **PR #12 on masterhq** (open draft) has Reports 26-33 ready — merge or cherry-pick.
4. **DEFINITIVE_INCIDENT_REPORT.md** (58KB) in malware-invasion is probably the single most important unmerged document.
5. **IMG_2877.jpeg** needs to be committed from the user's device — it's evidence of nss.peristor.com C2 at boot with no network cable.
6. **The 92MB of Windows Event Logs** in malware-invasion branches are raw evidence that should be preserved.
