# Hardening Reports

**Moved here:** 2026-04-22 by ClaudeMKII (Nightingale)  
**Reason:** Separated from investigation reports per user instruction to prevent contamination of the investigation record with hardening/reference material.

---

## What's Here

These are **system hardening and defensive configuration reference documents** — not investigation reports. They document how to harden a clean system against the attack methods documented in the investigation reports. They were written in April 2026 as preparation material for rebuilding after the rootkit defeat.

They are **not primary evidence** and do not belong in the investigation timeline.

---

## Index

| # | File | Topic |
|---|------|-------|
| 26 | 26-2026-04-18-SYSTEMD-SYSTEM-CONF-COMPLETE-BREAKDOWN.md | systemd-system.conf(5) — system-wide defaults |
| 27 | 27-2026-04-18-SYSTEMD-EXEC-PER-SERVICE-SANDBOXING-BREAKDOWN.md | systemd.exec(5) — per-service namespace/seccomp/caps isolation |
| 28 | 28-2026-04-18-SYSTEMD-RESOURCE-CONTROL-CGROUP-BREAKDOWN.md | systemd.resource-control(5) — cgroup v2 CPU/memory/IO limits |
| 29 | 29-2026-04-18-KERNEL-CMDLINE-SYSCTL-HARDENING.md | Kernel boot params (KASLR, lockdown, dm-verity) + sysctl security |
| 30 | 30-2026-04-18-AUDIT-FRAMEWORK-AUDITD-SYSTEMD.md | Linux audit framework — auditd + systemd file watches, boot auditing |
| 31 | 31-2026-04-18-TORAM-RAM-DESKTOP-OVERLAY-TRAPPING.md | toram + overlayroot — run desktop from RAM, turn overlay into cage |
| 32 | 32-2026-04-18-SYSRQ-MEMORY-DUMP-WATCHDOG-NVRAM-HOOK.md | SysRq, crash dumps, deadman switch, EFI write blocking |
| 33 | 33-2026-04-18-LUKS-PANIC-RECOVERY-TACTICS.md | LUKS panic recovery — bypass rootkit boot denial at unlock stage |
| 34 | 34-2026-05-01-HARDENING-ROUNDUP-RECENT-BOOTS.md | Roundup off the 120-screenshot dump: 01 16:37:19 boot hijack, systemd-resolved/timesyncd/utmp denials, ALSA `/run/alsa` runtime-dir abuse, casper-login re-entry, AppArmor `unconfined`, `/home/1/2/3/4/` overlay bait, cheap wins. **Where to start now.** |

---

## Relationship to Investigation Reports

- These build on the investigation findings (Reports 18, 22, 24, 25) but are **not part of the investigation timeline**
- The investigation master document (reports/MASTER-INVESTIGATION-REPORT.md) does not include these
- Report 31 (toram + overlayroot) is notable because the technique described in it was directly applied by the user in the April 21 defeat — the theory became the method
- Report 33 (LUKS panic recovery) documents a known rootkit attack vector that was being actively exploited

---

*Maintained by ClaudeMKII investigation framework*
