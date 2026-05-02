# Active Leads

**Mode:** Removal-focused. Existence is proven. We need it gone.

**Format:** Date + source + key points. Removal suggestions and "check this (reason)" flags only.

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
