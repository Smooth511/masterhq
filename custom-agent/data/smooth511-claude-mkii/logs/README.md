# logs/

Drop Windows Event Log (.evtx) files here for analysis.

## How to Use

1. Copy your .evtx file into this directory and commit it
2. Go to **Actions** → **Parse EVTX Event Log** → **Run workflow**
3. Enter the file path (e.g. `logs/yourfile.evtx`)
4. Set PIDs to hunt (e.g. `1052 3992`)
5. Download the JSON artifact from the workflow run

## Direct CLI Usage

```bash
pip install evtx
python3 tools/parse_evtx.py logs/yourfile.evtx output.json --hunt-pids 1052 3992
```

## Options

| Flag | Description |
|------|-------------|
| `--hunt-pids 1052 3992` | Search for specific PIDs in process event fields |
| `--event-ids 4688 7045` | Filter to specific event IDs only |
| `--all` | Export all events (not just security-relevant ones) |
| `--summary-only` | Print service installs and process creations only |
| `--search "svchost"` | Case-insensitive string search across all event data |

## Key Security Event IDs

| ID | Meaning |
|----|---------|
| 4688 | Process Created — PID, name, parent, cmdline |
| 4689 | Process Terminated |
| 7045 | Service Installed (System log) |
| 4697 | Service Installed (Security log) |
| 4698 | Scheduled Task Created |
| 4624 | Logon Success |
| 1102 | Audit Log Cleared ⚠️ |
| 5156 | Network Connection Allowed |

## Current Logs

| File | Description | Status |
|------|-------------|--------|
| `../logs1sthour/All hourlysave.evtx` | Mini-Tank-MKII first hour (2026-03-18) | 28,748 records — analyzed |
