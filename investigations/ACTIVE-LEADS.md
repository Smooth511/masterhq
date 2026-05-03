# Active Leads

**Mode:** Removal-focused. Existence is proven. We need it gone.

**Format:** Date + source + key points. Removal suggestions and "check this (reason)" flags only.

---

## 2026-05-03 — OEM Mint Install (New System State)

**Context:**
- Mint Linux installed in OEM mode — installer ran under oem user (uid ~29955)
- Install landed in `/home/oem` — OEM account is the bootstrap user, not a real user
- User has full root access from here
- This is the SAME machine as the rootkit investigation — prior context still applies
- `file_system_contents.txt` was referenced in comms but didn't arrive — run `tools/collect-system-state.sh` to generate it

**Check this:** With root access and the OEM user at uid 29955, check if the rootkit remapped its own user to this UID range (it remapped to uid/gid 1000 on previous installs per null-trap operation). The OEM uid being 29955 could be default OEM behaviour — OR it could be the rootkit already grabbed a foothold before the user could.

**Check this:** `/home/oem/.config/autostart/` and `/etc/oem*` — if rootkit is present it'll have hooks here already.

**Removal:** If the OEM setup is clean (rootkit not yet present): finish OEM setup creating a real user, then immediately run `collect-system-state.sh` as root before rebooting to capture the clean baseline.

---

## 2026-05-02 — GRUB Shell Screenshots (162 OCR'd, evidence/)

**Key points:**
- User spent 4 hours in GRUB shell, found rootkit scripts directly
- 162 screenshots captured and OCR'd — raw evidence in evidence/
- Confirms rootkit has pre-boot presence (pre-overlay, pre-kernel)

**Check this:** GRUB script content — if we can identify the loader entry point, we can potentially replace or poison it with a dummy that fails silently, breaking the boot chain before the overlay assembles. Need the actual script filenames and contents from the OCR.

**Check this:** Any UUIDs in the GRUB scripts — rootkit uses UUIDs to identify target partitions. If we get them we know exactly what it's mounting and potentially which partition to wipe or corrupt to break persistence.

---

*Append new entries above this line. Keep it short.*
