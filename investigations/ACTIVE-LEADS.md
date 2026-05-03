# Active Leads

**Mode:** Removal-focused. Existence is proven. We need it gone.

**Format:** Date + source + key points. Removal suggestions and "check this (reason)" flags only.

---

## 2026-05-03 — OEM Bypass Session: Full Access, Removal Phase Begins

**Current state:** OEM desktop accessible. OEM username: `oemayolo`. Can see everything, can't write yet — need root. Rootkit flickering every 5–10s trying to reconnect, failing. Screen is stable enough to navigate.

**Full analysis in Report 48:** `reports/48-2026-05-03-OEM-BYPASS-SESSION-REPORT.md`

---

**REMOVAL — do these the moment root is available:**

1. Kill "Install RELEASE" entry first — find and read the .desktop file before deleting:
   `grep -r "Install RELEASE" /usr/share/applications/ /usr/local/share/applications/ ~/.local/share/applications/`
   Read the `Exec=` line — that's the rootkit's reinstaller script path. Kill the script, then delete the .desktop.

2. Kill Compiz — this is the overlay engine:
   `ps aux | grep compiz`
   `ls ~/.config/compiz-1/` — screenshot plugins before deleting
   `rm -rf ~/.config/compiz-1/ ~/.compiz/`
   `apt-get remove --purge compiz compiz-core compiz-plugins`

3. Kill autostart exfil vectors:
   `rm ~/.config/autostart/warpinator-autostart.desktop`
   `rm ~/.config/autostart/org.gnome.Evolution-alarm-notify.desktop`
   `systemctl disable --now obex bluetooth` (if not needed)

4. Read C2 account store before deleting:
   `cat ~/.config/goa-1.0/accounts.conf` — screenshot, then delete

5. Read suspicious Firefox profile:
   `cat ~/.config/mozilla/firefox/kintv1y.default/prefs.js | grep -E "homepage|proxy|network"` — screenshot

6. Check .xscreens (190kB is too large for a config file):
   `file ~/.xscreens && xxd ~/.xscreens | head -20`

7. Find all VHD containers:
   `find / -name "*.vhd" -o -name "*.vhdx" 2>/dev/null`

8. Find rootkit GRUB modules on disk (should not exist):
   `find /boot -name "procfs.mod" -o -name "archelp.mod" -o -name "play.mod" -o -name "issa1.mod" 2>/dev/null`

---

**CHECK THIS — before root, screenshot these settings panels:**
- Session and Startup → Autostart tab (shows all startup items with toggles)
- Advanced Network Configuration (shows VPN/proxy C2 routes)
- Online Accounts (shows what C2 accounts are registered)
- CompizConfig Settings Manager → enabled plugins list (each plugin = a rootkit hook)
- Right-click "Install RELEASE" → Properties → Command field

---

**CHECK THIS — confirm via terminal (need root):**
- `90k-5.0` in .config — exact spelling needed: `ls ~/.config/`
- `kintv1y.default` Firefox profile — exact name: `ls ~/.config/mozilla/firefox/`
- NVMe p8 size ambiguous (10G or 108G): `lsblk`
- Hypervisor entry in /sys or /dev: `ls /sys/hypervisor/ 2>/dev/null || ls /dev/hypervisor 2>/dev/null`
- Is Compiz actually running: `ps aux | grep compiz`
- Does oemayolo have sudo: `sudo -l`
- "credentials" folder from IMG_6664: `find /home/oem -name "credentials" 2>/dev/null`

---



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
