# Master — Project 12 Forensic Documents

This folder contains the master organised document set for Project 12 (iOS + Windows rootkit investigation).

---

## Primary Documents

| Document | Purpose | Audience |
|----------|---------|----------|
| `Master-no-redacts.md` ⚠️ | **Full report with all identifiers** — device serial, IMEI, iOS build, network addresses, IoCs, and Apple PSIRT submission template. **NOT stored in this repository** (gitignored). Distribute via encrypted channel / secure vault only. | Apple PSIRT, national CERTs, authorised investigators — **RESTRICTED** |
| [`Public-no-identifiers.md`](Public-no-identifiers.md) | **Public report — no device identifiers** — full technical findings and IoCs, all personal/device identifiers removed | Public, security researchers, vendor disclosure |

> ⚠️ **`Master-no-redacts.md` is in `.gitignore`** and will never be committed to this
> repository. The full-identifier master report must be generated locally and distributed
> exclusively through an encrypted, access-controlled channel (e.g. Signal, encrypted email,
> or a private secure vault). Committing it — even to a private repo — risks permanent
> exposure if repository visibility ever changes.

---

## Final Reports

The [`Final-Reports/`](Final-Reports/) subfolder contains the formal forensic analysis documents:

| Document | Description |
|----------|-------------|
| `FORENSIC_ANALYSIS.md` | Comprehensive forensic analysis — full detail, restricted circulation |
| `Forensic_diagnosis_annotated.md` | Annotated review copy with veracity labels and evidence requests |
| `Forensic_diagnosis_redacted.md` | **Fixed public-safe copy** — all identifier tokens moved to Appendix A |
| `findings_summary.md` | Executive findings summary with veracity assessment table |

---

## Context Documents

The [`Context-Documents/`](Context-Documents/) subfolder contains session handover and context
documents that were created between investigation sessions to preserve continuity:

| Document | Description |
|----------|-------------|
| `Ioshandover.md` | iOS First Contact — session handover brief (March 12) |
| `Firstcontact.md` | iOS First Contact — context brief (alternate version) |
| `Evtxinvestigation.md` | EVTX Analysis Addendum — Windows session handover with retractions |
| `Investigation-summary.md` | ⚠️ Active Incident Investigation Summary — **contains real device identifiers** |
| `Project12rootkit.md` | ⚠️ Rootkit Session Handoff Save File — **contains real device identifiers** |
| `TCP-UDP-Countermeasure-Defense-Strategy.md` | Full defense architecture — Feb 24–27, 2026 TCP/UDP countermeasure strategy, attack timeline |
| `Registry-Defense-Configuration.md` | **Registry-level defense config** — all HKLM/HKCU paths for UDP block, TCP QoS throttle, 32 GB paging file, GPO settings, and forensic extraction commands |

> ⚠️ `Investigation-summary.md` and `Project12rootkit.md` contain real device identifiers
> (S/N, IMEI, phone number). Keep this repository **private**. See
> `Context-Documents/README.md` for full handling guidance.

---

## Classification Guide

| Label | Meaning |
|-------|---------|
| **RESTRICTED** | Contains device identifiers, IMEI, serial numbers, certificates — do not share publicly |
| **Public** | No device identifiers — safe for public distribution |
| Investigation Use Only | Contains investigation methodology and session notes — not for external sharing without review |
