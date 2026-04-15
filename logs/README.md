# Operational Logs

Session logs, lockdown records, compliance reports, and operational documentation.

*Reorganized 2026-04-03 by MK2*

## Contents

### Lockdown (March 2026)
- `LOCKDOWN-MASTER-LOG.md` — Primary lockdown log
- `LOCKDOWN-FINAL-REPORT.md` — Final lockdown report
- `LOCKDOWN-NOTICE.md` — Lockdown notice
- `LOCKDOWN-LIMBO-LOG.md` — Limbo period log
- `LOCKDOWN-REPO-LOG-Claude-MKII.md` — Repo-specific lockdown log
- `LOCKDOWN-COMPLIANCE-REPORT-2026-03-23.md` — Compliance verification
- `POST-LOCKDOWN-REPORT-2026-03-23.md` — Post-lockdown analysis
- `2026-03-23-lockdown-incident-summary.md` — Incident summary

### Sessions
- `SESSION-LOG-2026-03-20.md` — Session log
- `SESSION-LOG-2026-03-20-activation.md` — Phantom activation log
- `SESSION-REVIEW-2026-03-25-vscode-connection.md` — VSCode session review
- `seeding-session-log.md` — Original seeding session

### Operations
- `PR-RESOLUTION-REPORT-2026-03-23.md` — PR conflict resolution

## EVTX Parser

To parse Windows Event Logs, use the EVTX parser:

```bash
pip install evtx
python3 tools/parse_evtx.py <file.evtx> output.json --hunt-pids 1052 3992
```

See `tools/` for full documentation.
