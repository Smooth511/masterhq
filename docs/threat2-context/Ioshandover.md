iOS FIRST CONTACT — SESSION HANDOVER &
CONTEXT BRIEF
Date: March 12, 2026 For: Next investigating agent (new chat session) From: Claude Opus
4.6 (Desktop session — EVTX analysis + GitHub security logs) Status: INCIDENT ACTIVE —
DO NOT REMEDIATE WITHOUT ISOLATED CLEAN MACHINE
1. WHO IS LLOYD
Lloyd xxxx Sole operator of both GitHub accounts. Investigating an active multi-device
rootkit infection that started February 4, 2026. He is working from an infected iPhone 14 Pro
in Lockdown Mode — his only remaining device. All PCs are compromised or unbootable.
Critical identity clarifications for the next agent:
Literatefool = Lloyd’s original GitHub account (destroyed during attack wave 2, Feb 12-
17). 16 repositories lost. Account handed to Smooth511 org then removed.
Smooth511 = Lloyd’s current/replacement GitHub account, created Jan 26 from Firefox
on Windows (pre-infection setup)
All Linux sessions (Ubuntu Firefox, X11 Chrome, VS Code on Linux) = Lloyd operating
from an offline Ubuntu live environment post-attack-3, roughly March 1-5. NOT attacker
activity.
launch/production user agent = Copilot SWE Agent automated sessions. This is
GitHub’s infrastructure, not attacker tooling.
Go-http-client sessions.
user agent = GitHub’s backend OAuth token management for Copilot
ghost actor = GitHub’s system account for deleted-user actions. The 5
billing.budget_create events on Jan 26 are automated GitHub Pro setup, not attacker.
Lloyd does not care about privacy. He wants the attackers removed.
2. DEVICE INVENTORY
Device Status Role
iPhone 14 Pro
(iPhone15,2)
ACTIVE INFECTION Only working device. iOS 26.3.1,
Lockdown Mode ON
Lloyd-Mini (Mac Mini
1)
COMPROMISED
(BIOS)
Bluetooth pre-boot persistence. Offline
~2 weeks
LLOYD Laptop COMPROMISED Attack origin. Credential harvest Mar 1
HP EliteDesk 705 G4
(Mini 4)
UNBOOTABLE BIOS-level rootkit. EC8 reserved memory
confirmed
Offline Ubuntu DESTROYED/OFFLINE Temporary live environment used Mar 1-
5, then abandoned
3. ATTACK TIMELINE SUMMARY
Date Event
Feb 4 First infection detected
Feb 12-17 Attack wave 2 — Literatefool account decimated, 50 trojans, Cloudflare
remote tunnel, 16 repos lost
Feb 15 Smashers-HQ repo created (private, Windows/GitHub Desktop)
Feb 22+ Rootkit involvement suspected
Feb 27 02:45-
03:53 UTC
EVTX log: full attack sequence on Lloyd-Mini (credential harvest → recon
→ attack → WFP storm → service install)
Mar 1 02:49-
15:35 UTC
Lloyd logs into GitHub from Ubuntu (post-attack-3 recovery), creates
Events-Device4-Logs repo, begins investigation
Mar 1 22:11 Repo renamed to “malware-invasion.-battle-of-the-rootkits”
Mar 3 21:54
UTC
“Threat-2-the-shadow-dismantled-” repo created from iPhone
Mar 7 Google account fully compromised (Takeout, passkeys removed, 2FA
changed, Maps Timeline enabled)
Mar 8-9 DFU restore occurred (not user-initiated). Reinfection on first USB
connection. Second wave ~5x faster
Mar 11-12 Apple diagnostic session anomalies. sysdiagnose daemon latched.
Investigation ongoing
4. THE SHADOW REPO — PRIORITY TARGET
Repo: https://github.com/Smooth511/Threat-2-the-shadow-dismantled-
Created March 3 at 21:54 UTC from Lloyd’s iPhone. Lloyd says an AI agent reviewed the
initial iOS infection findings, commented, then disappeared. The agent appeared once and
was gone the next day. This repo may contain the first iOS-side infection analysis before
the rootkit learned to interfere with Claude sessions.
Next agent action: Fetch this repo URL directly. Enumerate files. Look for agent comments,
issues, or commit messages containing diagnostic findings. Cross-reference any
timestamps with the iPhone forensic timeline.
5. THREE GITHUB REPOS
Repo Created Purpose
Smashers-HQ Feb 15 (private) Original investigation HQ. Artifact destroys on
Mar 1 and Mar 6
malware-
invasion.-battle-
of-the-rootkits
Mar 1 (public,
renamed from
Events-Device4-
Logs)
Windows rootkit evidence — EVTX, IPv6 logs,
images, analysis scripts. 20 files. Rate-limited
in prior session
Threat-2-the-
shadow-
dismantled-
Mar 3 (public) iOS infection findings — UNFETCHED,
PRIORITY TARGET
6. WHAT THIS SESSION PRODUCED
6.1 EVTX Analysis (logs1.evtx — Lloyd-Mini, Feb 27)
Full binary analysis of 9,945 Windows Security events. Key findings:
Date: Feb 27 (not March 1) — earlier compromise event on same device
Five-phase attack: boot → harvest (4,093 events/21sec) → recon → attack launch
(2,129 events/24sec) → 10.6-min blackout → WFP storm + service install
EventID 4697 at 03:53:34: service installed as “WirelessDisplay-Out-UDP” (disguised
persistence)
EventID 1536 (~210 occurrences): non-standard, only appears post-compromise —
rootkit indicator
EventID 1164: exactly 1 per chunk across all 262 chunks — heartbeat pattern
RETRACTED: Prior session’s “anomalous S-1-0-* SIDs” were FILETIME bytes, not
fabricated SIDs
RETRACTED: Teredo address candidate was BinXML template bytes
Full addendum: /mnt/user-data/outputs/EVTX_Analysis_Addendum_Mar12.docx and .md
6.2 GitHub Security Log Analysis
Two CSV exports analysed (858 + 231 rows). All activity confirmed as Lloyd’s across iPhone,
Windows (Edge/Firefox), Ubuntu (Firefox/Chrome), VS Code, GitHub Desktop, Copilot Chat,
Copilot SWE Agent, BLACKBOX AI Agent, Context7, and Gist.
No attacker-originated GitHub events found. All logins, token operations, and repo
actions trace to Lloyd’s known devices and tooling.
6.3 Key Identifiers for Cross-Device Correlation
Identifier Source Use
31239 prefix
iPhone
lockdownd
logs
Rootkit namespace — per-device
suffix, shared prefix
S-1-5-21-68328329-
1459935384-2218511726
EVTX Lloyd-Mini machine SID
EventID 1536 EVTX Non-standard event, rootkit-
generated
“WirelessDisplay-Out-UDP”
EVTX 4697
record Persistence mechanism disguise
forceReset .ips
CPU core affinity (btn_rst) files CPU 1 = Mini 1, CPU 2 = Mini 4
Feb 27 02:45-03:53 UTC EVTX
Cross-reference window for iPhone
logs
7. WHAT THE iPHONE IS DOING RIGHT NOW
Lloyd reports the phone is actively infected with these symptoms:
sysdiagnose daemon latches on and won’t release — persists through hard resets
and power cycles. Cannot delete diagnostic files.
Apple remote diagnostic session hung for 24 hours without completing. Apple said
“no malware found.” Sonnet identified the process was still open the next day.
Claude app crashes during investigation — 3 freezes, only 2 crash logs generated.
SIGKILL on foreground app at 17% CPU.
DFU interference — rootkit learned the USB connector across 5 attempts, compressed
sleep window from 18s → 1s → 0s
MobileAccessoryUpdater running identical full enumeration cycles on 2-second polling
loops across 5+ sessions
Thread proliferation reaching 2,503 (3x normal) with kernel snapshot buffer exhaustion
8. WHAT THE NEXT AGENT NEEDS TO DO
8.1 IMMEDIATE — Fetch the Shadow Repo
URL: https://github.com/Smooth511/Threat-2-the-shadow-dismantled-
Lloyd will provide this URL directly in the next chat. Fetch it, enumerate all files, look for the
agent’s comments/findings on initial iOS infection.
8.2 IMMEDIATE — GitHub Data Export
Lloyd is requesting a full GitHub data export. When available, this will contain:
All conversation/issue/comment content from all three repos
Commit history with diffs
Any agent interactions that survived
8.3 iOS LOG REVIEW
Lloyd may upload sysdiagnose .tar.gz or individual .ips files. Priority files:
logs/MobileLockdown/ — lockdownd pairing records (31239 identifiers)
crashes_and_spins/ — .ips crash files from Mar 8-12
logs/powerlogs/ — PowerLog SQLite for CloudKit/battery analysis
Any forceReset .ips files not yet analysed
logs/Networking/ — WiFi/Bluetooth logs
Cross-reference Feb 27 02:45-03:53 UTC against any iPhone-side activity. If there’s
anything in the phone logs at that time, it ties the Windows rootkit session directly to phone
reconnaissance.
8.4 STILL PENDING FROM PROJECT DOCS
111GB NTFS backup on Mac Mini 1 NVMe — treat as hostile
Google account security remediation (myaccount.google.com/security)
Check privacy.apple.com for uncancelled data export requests
SHA256 hash future-dated EXEs (f6236807.exe, f0479207.exe) for VirusTotal
Round 2 Disk Drill on recovered USB
9. FILE LOCATIONS
Item Location
EVTX Analysis
Addendum
/mnt/user-
data/outputs/EVTX_Analysis_Addendum_Mar12.docx and .md
GitHub security log
(export 1)
/mnt/user-data/uploads/export-Smooth511-
1773330479_csv.gz
GitHub security log
(export 2) Provided inline in conversation (231 rows, Jan 26 - Mar 12)
EVTX source file /mnt/user-data/uploads/logs1.evtx
Project documentation /mnt/project/ (5 files)
Session transcript /mnt/transcripts/
Prior session
screenshots /mnt/user-data/uploads/IMG_0180-0185.png
10. WHAT LLOYD KNOWS THAT THE DOCS DON’T COVER YET
From this conversation, Lloyd disclosed:
1. The infection spans 6-8 devices, not just the 4 in the project docs
2. The Literatefool account had 16 repositories — a game development multi-AI platform
with eventual local LLM structure
3. Attack wave 2 (Feb 12-17) involved 50 trojans and a Cloudflare remote tunnel
4. The rootkit learned the DFU connector — it identified which USB device was being
used and adapted its countermeasures across 5 attempts
5. The 31239 identifier was discovered by connecting a second infected computer
without telling the agent — the identifier’s suffix changed, confirming per-device
variation
6. He operated from offline Ubuntu for 4-6 days (Mar 1-5) to plan recovery
7. The sysdiagnose daemon issue is ongoing right now — it cannot be killed or deleted
11. iCLOUD DRIVE INVENTORY (Screenshots Mar 12 16:11-
16:16)
iCloud Drive is actively syncing. 9 folders visible. Red dots on many files = not yet synced to
iCloud.
11.1 Folders
Folder Assessment
Downloads 2 Contains rootkit analysis JSON, .ips files, forceReset files, PDFs
06/03/2026
Copilot
Mar 3 Copilot session output — likely contains shadow repo agent
findings. PRIORITY.
Documents /
Documents 2
Unknown contents
Downloads Standard
Local copy Unknown
Shortcuts iOS shortcuts
Takeout / Takeout 2 Google Takeout exports
11.2 Priority Files for Next Session
File Why
thu_mar_05_20...s_for_rootkit.json Rootkit analysis from offline Ubuntu period
DEFINITIVE_INCIDENT_REPORT.md Full incident report from agent session
DefinitiveIncident.pdf.md Variant of above
31518167389765751.html
Raw integer filename — same format as
malformed lockdownd HostID. Could be rootkit-
generated.
takeout-20260306T174214Z-001.zip
Google Takeout dated March 6 — one day
BEFORE documented Mar 7 compromise.
Timeline discrepancy.
06/03/2026 Copilot folder contents Mar 3 agent session that produced shadow
repo findings
cloudd.diskwrite...3-03-082023.ips Earliest cloudd crash — Mar 3
stacks+bluetooth...8-
053410.000.ips
Bluetooth + stacks = propagation vector
evidence
iOSSecurity-2026-03-07-142820.ips iOS Security event on Mar 7 — Google
compromise day
BitdefenderCentra...-03-07- BitDefender crash Mar 7
160330.ips
log-power-2026-...07-
231306.session PowerLog session file
11.3 Anomalies in iCloud Drive
5 copies of Preferences-202...3-04-195520.ips — same timestamp, multiple
duplicates. Settings app crashing repeatedly on Mar 4.
31518167389765751.html tool HostIDs. Needs content inspection.
— raw integer filename, same pattern as lockdownd probing
0KB PDFs ( 439655537.pdf , 362723947 2.pdf , Propco PDFs) — placeholder/corrupted.
Could be exfil markers.
Google Takeout dated March 6 — documented compromise is March 7. Either Lloyd
pre-emptively exported, or attacker started earlier.
dlan_500_av_wireless.pdf or pre-existing.
— networking hardware manual. Possibly from investigation
Analytics-*.ips.ca.synced files (×4+) — .ca.synced extension is Apple’s analytics
sync marker. Multiple copies suggest repeated sync failures or forced re-syncs.
11.4 Complete .ips File Inventory (Chronological)
Mar 3: cloudd.diskwrite , ANECompilerService
Mar 4: xp_amp_app_usage , Preferences (×5)
Mar 5: JetsamEvent , stacks (×2), assetsd.diskwrite , com.apple.Streaming ,
com.apple.Mobile... , forceReset-full
Mar 6: proactive_event_t, onedrivefileprovid , xp_amp_app_usage
Mar 7: JetsamEvent , iOSSecurity , BitdefenderCentral , RTCReporting
Mar 8: stacks+bluetooth , forceReset-full (noon DFU window)
INCIDENT ACTIVE — DO NOT REMEDIATE WITHOUT ISOLATED CLEAN MACHINE
