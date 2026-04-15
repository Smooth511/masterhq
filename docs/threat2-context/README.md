# Context Documents

These documents were created between investigation sessions to preserve continuity and provide
context for the next investigating agent or session. They are session handover notes and
investigation save files — not formal forensic reports.

| Document | Date | Description |
|----------|------|-------------|
| [`Ioshandover.md`](Ioshandover.md) | March 12, 2026 | iOS First Contact — session handover brief. Covers device inventory, attack timeline, and the Shadow repo context. (Prepared by an AI assistant session — model attribution from source document is unverified.) |
| [`Firstcontact.md`](Firstcontact.md) | March 12, 2026 | iOS First Contact — alternate/parallel handover brief. Same context as above. |
| [`Evtxinvestigation.md`](Evtxinvestigation.md) | March 12, 2026 | EVTX Analysis Addendum & Session Handover. Documents Windows binary EVTX analysis, retractions of false positives, and confirmed attack findings. |
| [`Investigation-summary.md`](Investigation-summary.md) | March 12, 2026 | Active Incident Investigation Summary. Comprehensive device inventory, confirmed rootkit capabilities, PowerLog/CloudKit analysis, and open questions. ⚠️ **Contains real device identifiers (S/N, IMEI, phone number).** |
| [`Project12rootkit.md`](Project12rootkit.md) | March 12, 2026 | Rootkit Session Handoff Save File. Component identification (BIOS, Windows kernel, iOS layers), threat actor assessment, and critical forensic discoveries. ⚠️ **Contains real device identifiers (S/N, IMEI).** |
| [`TCP-UDP-Countermeasure-Defense-Strategy.md`](TCP-UDP-Countermeasure-Defense-Strategy.md) | March 16, 2026 | Full defense architecture — UDP block, TCP bait tunnel, 32 GB paging file memory trap, attack timeline analysis. Feb 24–27, 2026 countermeasure strategy. |
| [`Registry-Defense-Configuration.md`](Registry-Defense-Configuration.md) | March 16, 2026 | **Registry-level defense configuration reference.** All HKLM/HKCU paths for UDP block, TCP QoS throttle, 32 GB paging file, Computer GPO, and User GPO. Includes offline forensic extraction commands and rootkit registry persistence documentation. |

> ⚠️ **Security notice:** `Investigation-summary.md` and `Project12rootkit.md` contain real
> device identifiers (serial number, IMEI, iOS build, phone number). These documents existed
> in the repository prior to this reorganisation. **Do not share these files publicly and ensure
> this repository remains private.** If public disclosure is required, use
> [`Public-no-identifiers.md`](../Public-no-identifiers.md), which contains no device PII.
> If this repository must become public, these two files should be removed from Git history
> using `git filter-repo` before changing visibility.
