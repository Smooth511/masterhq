# Context Directory

This directory holds system state dumps so agents don't need to be re-briefed every session.

## Files

| File | What it is | How to update |
|------|-----------|---------------|
| `SYSTEM-STATE.txt` | Live dump of the OEM Mint install state — filesystem, users, mounts, partitions, processes | Run `tools/collect-system-state.sh` as root, commit the output here |

## How to use

1. On the OEM Mint machine, run as root:
   ```
   bash tools/collect-system-state.sh > context/SYSTEM-STATE.txt
   ```
2. Commit and push:
   ```
   git add context/SYSTEM-STATE.txt && git commit -m "update: system state dump" && git push
   ```
3. Every agent session loads this automatically — no re-explaining needed.

## Agents

Agents: if `context/SYSTEM-STATE.txt` exists, **load it before responding to any question about the system**. Treat it as authoritative current state.
