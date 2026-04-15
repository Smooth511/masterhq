# Evidence Directory

This directory contains all evidence from the ongoing malware/rootkit investigation.

*Reorganized 2026-04-03 by MK2*

## Structure

```
evidence/
├── raw/                    # Untouched source material — raw evidence drops
│   ├── THEBULLETFROMSMOKINGUN/  # Apr 2 ASUS investigation (photos, chatlogs, OCR)
│   ├── BINGO/                    # BINGO evidence (screenshots, video, chat)
│   ├── logs1627/                 # System logs rip (80 files, 78MB)
│   ├── logs1sthour/              # First-hour EVTX capture
│   ├── logslinux29/              # Linux raw logs
│   ├── LinuxRaw25/               # Linux raw data PDFs + text
│   ├── CodeSmooth/               # Code recovery evidence
│   ├── VSCODE/                   # VSCode USB evidence
│   ├── linux-logs-screenshots/   # Investigation screenshots + ErrorLogs
│   └── (journals, images, PDFs, misc)
│
├── analysis/               # Individual evidence writeups (mostly 2026-03-19)
│   ├── vindication-log-2026-03-19.md
│   ├── malware-analysis-2026-03-19.md
│   ├── registry-analysis-*.md
│   └── (18 total analysis files)
│
└── README.md               # This file
```

## Reports

Full investigation reports that synthesize evidence are in `../reports/` (numbered 01-20 chronologically).

## Evidence Categories

- **Registry** — Windows registry exports and analysis
- **Network** — Connection logs, IP addresses, traffic analysis
- **Process** — Process trees, PIDs, parent-child relationships
- **Filesystem** — Suspicious files, timestamps, locations
- **Logs** — EVTX, CBS logs, system logs, dmesg, journals
- **ACPI/Firmware** — SSDT tables, WPBT, EFI variables
- **Screenshots** — iPhone photos of terminal output, BIOS, error screens

---

*Maintained by ClaudeMKII investigation framework*
