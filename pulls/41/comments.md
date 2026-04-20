## ADDITION REQUIRED — Cross-Platform Timing Correlation (Finding 8)

The coding agent MUST add the following as **Finding 8: Cross-Platform Phone-Home Timing Correlation** in the evidence report being created.

### The Pattern

From prior Windows investigation (documented in MASTER_REPORT), the attacker's malware phones home at **Day 3** and **Day 19** after initial injection. These same intervals appear on the Linux side:

| Day | Windows Side (MASTER_REPORT) | Linux Side (This Session) |
|-----|-----|------|
| Day 0 (Aug 8) | Injection during DISM phase | Kernel placed on machine, journal anchored to Aug 8 |
| Day 3 (Aug 11) | First phone-home callback | First callback window |
| Day 17 (Aug 25) | — | Kernel hash first appears on VirusTotal |
| Day 19 (Aug 27) | Second phone-home callback | `force-complain/usr.sbin.sssd` symlink created — AppArmor enforcement on enterprise auth daemon deliberately weakened |

### Key Observations

1. **Aug 27 2024** — the exact date on the `force-complain/usr.sbin.sssd` symlink matches the Day 19 phone-home window from Windows. The sssd AppArmor weakening was not maintenance — it was the 19-day callback triggering the next attack stage.

2. **Aug 25 (Day 17)** — VirusTotal first-seen for the kernel hash is 2 days before the Day 19 callback. Either the VT submission was a check by the attacker ("is this binary burned yet?") or their scanning infrastructure picked it up automatically.

3. **Same cadence, cross-platform** — identical timing patterns on Windows and Linux confirm a single operator running one operation across two OS targets, with the `CN=grub` MOK certificate as the firmware bridge between them.

### Classification: 🔴 CRITICAL — confirms single-operator cross-platform persistence with coordinated timing

This finding connects the Windows-side evidence (DISM/Synergy, PushButtonReset hijack, MIG controller UIDs) to the Linux-side evidence (MOK cert, kernel swapping, AppArmor weakening) through matching callback schedules.