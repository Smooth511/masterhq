# Investigation Reports

Chronologically numbered investigation and analysis reports. Each report synthesizes evidence from `../evidence/`.

*Reorganized 2026-04-03 by MK2. Hardening reports separated 2026-04-22 by ClaudeMKII/Nightingale.*

---

## Master Document

**[MASTER-INVESTIGATION-REPORT.md](MASTER-INVESTIGATION-REPORT.md)** — Consolidated single source of truth covering Reports 19–37 (non-hardening). Resolves all contradictions, flags all known fake/incorrect claims, lists all outstanding investigations, includes CORRECTED/REMOVED appendix. Written 2026-04-22.

---

## Hardening Reports

Reports 26–33 (system hardening reference guides) have been moved to the **[hardening/](hardening/)** subdirectory. They are not part of the investigation timeline.

---

## Report Index

| # | Date | Report | Focus |
|---|------|--------|-------|
| 01 | 2026-03-18 | Push Button Reset Analysis | PBR partition analysis |
| 02 | 2026-03-18 | Investigation Report | Initial HP investigation |
| 03 | 2026-03-19 | HP Evidence Master Report | Consolidated HP evidence |
| 04 | 2026-03-20 | Security Audit Report | Security audit findings |
| 05 | 2026-03-26 | Agent-1 Investigation | Linux log agent investigation |
| 06 | 2026-03-26 | Agent5 Investigation | 5-agent review |
| 07 | 2026-03-26 | Linux Agent1 Investigation | Linux-specific agent report |
| 08 | 2026-03-26 | 5-Agent Review | Multi-agent consolidated review |
| 09 | 2026-03-26 | UEFI-MOK Kernel Evidence | UEFI/MOK/kernel findings |
| 10 | 2026-03-26 | MK2 Log Analysis | MK2's own log analysis |
| 11 | 2026-03-27 | Attack Evolution | Attack model evolution |
| 12 | 2026-03-27 | Screenshot Analysis | Visual evidence analysis |
| 13 | 2026-03-29 | .gitignore Sabotage | Agent sabotage investigation |
| 14 | 2026-03-30 | BINGO Evidence Catalog | BINGO evidence cataloging |
| 15 | 2026-03-30 | TheLink Comprehensive Analysis | TheLink full analysis |
| 16 | 2026-03-30 | TheLink Gap Analysis | Gaps in TheLink evidence |
| 17 | 2026-04-01 | logs1627 Analysis | System logs analysis (80 files) |
| 18 | 2026-04-01 | **Comprehensive Rootkit Report** | **MASTER REPORT** — all 12 sources |
| 19 | 2026-04-02 | THEBULLETFROMSMOKINGUN Report | ASUS investigation report |
| 20 | 2026-04-02 | THEBULLETFROMSMOKINGUN Analysis | ASUS deep technical analysis |
| 21 | 2026-04-11 | AICHAT + OCR220 Analysis | AI chat review, OCR220SS, dpkg cross-reference |
| 22 | 2026-04-11 | **Pre-Overlay Breach** | **Initramfs tactical breach, inwahnrad injection proof, Ventoy boot chain dissection** |
| 23 | 2026-04-14 | Cross-Repo Verification | Cross-repo evidence verification |
| 24 | 2026-04-14 | Recovery Root Shell Tactical Command Analysis | Command-by-command forensic review of OCRRoot sessions |
| 25 | 2026-04-17 | **GNU Binary Reconstruction Theory** | **Core dump deleted libs, kernel version changes, user's CRT extraction experiment, binary-encoded persistence theory** |
| 26 | 2026-04-18 | systemd-system.conf(5) Complete Breakdown | System-wide systemd defaults — foundation for hardening series |
| 27 | 2026-04-18 | systemd.exec(5) Per-Service Sandboxing | Namespace isolation, seccomp, capabilities per service |
| 28 | 2026-04-18 | systemd.resource-control(5) Cgroup Controls | CPU/memory/IO limits per service via cgroups v2 |
| 29 | 2026-04-18 | Kernel Command-Line & sysctl Hardening | Boot params (KASLR, lockdown, dm-verity) + sysctl security |
| 30 | 2026-04-18 | Linux Audit Framework: auditd & systemd | File watches, syscall monitoring, boot chain auditing |
| 31 | 2026-04-18 | **toram, overlayroot & Defensive Trapping** | **Run desktop from RAM + turn overlay into monitored cage** |
| 32 | 2026-04-18 | **SysRq Memory Dump, Watchdog & NVRAM Hook** | **Crash dumps, deadman switch, EFI write blocking — the trap payoff** |
| 33 | 2026-04-18 | **LUKS Panic Recovery Tactics** | **Kernel panics at LUKS unlock — bypassing rootkit boot denial, breathing room strategies** |
| 34 | 2026-04-21 | **🏆 /cow Overlay Kill: Bait, Destroy, Loot** | **First live capture of rootkit's operational OverlayFS layer — Casper scripts, captured passwords, full persistence tooling extracted from /cow/work/upper** |
| 34 | 2026-04-21 | **🔥 OVERLAY BREACH — Root FS Overlay Confirmed + Loot Attempt** | **`overlay / overlay rw 0 0` in fstab CONFIRMED. Real layer accessed. Shadow file copied. Timeshift + snapshots + casper scripts found. OOM kill + fake NVMe disconnect countermeasures triggered.** |
| 35 | 2026-04-21 | **💀 GRUB SHELL DEFEAT — Real Partition Exposed Pre-Overlay** | **`ls (hd0,gpt4)/` from GRUB shell exposes rootkit's dedicated data partition BEFORE any overlay assembles. ~45 fake `install-logs-*` dirs with impossible 2009/2010 timestamps. `yoink/` dir found — contents unconfirmed, see MASTER report §5.1.** |
| 36 | 2026-04-21 | **🎉 THE DEFEAT SESSION — 1200-Panel Bombardment, Rootkit UI Collapsed** | **User DDoS'd rootkit's panel-based overlay by loading 1200 panels → cairo/GSettings/notification daemons cascaded into failure → overlay couldn't reassemble fast enough to hide real filesystem → 26 images captured in 21 minutes as raw filesystem came through. Payback for the Teredo tunnel attack. Panel-overload is now a documented attack vector against rootkit UI overlays.** |
| 37 | 2026-04-21 | **Rooty VT Console & Pre-GRUB Bootloader Hijack** | **Rootkit runs a VT (tty7) that intercepts bootloader input BEFORE GRUB renders — captured via rooty console dumps and live-session rename test (Bernard → Mike → Poppy → `wanker`/`lloyd2`). Rootkit has embedded AI/LLM instance + drops iOS files cross-device. Supersedes earlier `wanker user` draft.** |

## Evaluations

The `evaluations/` subdirectory contains meta-analysis and process documents:
- Skill evaluations
- Status/progress updates
- PR-related documentation

---

*Maintained by ClaudeMKII investigation framework*
