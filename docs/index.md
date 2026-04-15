# Docs Index — Project 12 (Threat-2-the-shadow-dismantled-)

This folder contains consolidated reports produced from the repository sweep.

---

## Reports

| Document | Description |
|----------|-------------|
| [`feb-24-27-2026-tcp-udp-memory-buffer-countermeasures.md`](feb-24-27-2026-tcp-udp-memory-buffer-countermeasures.md) | **Primary report** — Comprehensive record of the TCP/UDP memory buffer countermeasures employed Feb 24–27, 2026. Covers defense architecture (three-tier wall, UDP block, TCP 2 KB/s bait, 32 GB paging file), full attack timeline with EVTX evidence (03:00 initiation, 03:42 first wave), registry/GPO/firewall configurations and paths, bandwidth/overflow calculations, rootkit hostile registry entries, and source file index with commit SHAs. |

---

## Source Documents (in `Master/Context-Documents/`)

| File | Contents |
|------|----------|
| [`TCP-UDP-Countermeasure-Defense-Strategy.md`](../Master/Context-Documents/TCP-UDP-Countermeasure-Defense-Strategy.md) | Full defense architecture and attack timeline |
| [`Registry-Defense-Configuration.md`](../Master/Context-Documents/Registry-Defense-Configuration.md) | Registry paths, values, and forensic extraction commands |
| [`Evtxinvestigation.md`](../Master/Context-Documents/Evtxinvestigation.md) | EVTX binary analysis — 9,945 event records confirming the defense |

---

*Repository:* `Smooth511/Threat-2-the-shadow-dismantled-`  
*Status:* ACTIVE INCIDENT — keep repository **private** (some context documents contain real device identifiers).
