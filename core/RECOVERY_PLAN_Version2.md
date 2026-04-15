# Focused Recovery & Documentation Plan (compact update)

Purpose
- Minimal, action-focused checklist and prioritized artifact targets for quick on-screen use from grub> or in a live Ubuntu session. I will update this file with new artifacts whenever you paste outputs you want added.

Log line (one-line per artifact — copy locally)
ID | PRI(1-5) | Found | Path | Time(UTC) | Note

Top 5 priority artifact targets (minimal, do these first)
1. Screenshots / Images (highest value)
   - Why: visual timeline, user context, attacker UI evidence.
   - Common paths (grub): 
     - insmod part_msdos; insmod ntfs; ls (hd1,msdos1)/Users/*/Pictures/
     - fallback: ls (hd1,msdos1)/Users/*/Desktop/
2. Registry tools & hives / regedit.exe
   - Why: attacker may drop custom reg tools or hive snapshots.
   - Common paths:
     - ls (hd1,msdos1)/Windows/System32/  (look for regedit.exe)
     - ls (hd1,msdos1)/Backup/Windows/System32/
3. Primary logs / EVTX / analysis scripts
   - Why: timeline, event correlation, attacker actions.
   - Common paths:
     - ls (hd1,msdos1)/Windows/System32/winevt/Logs/
     - ls (hd1,msdos1)/**/logs1.evtx  (use explicit paths if grub lacks globbing)
     - look for analyse_logs.py, logs1.all.xml
4. Boot artifacts / bootmgr / BCD / EFI
   - Why: boot persistence, chainloaders, EFI files.
   - Common commands:
     - insmod part_msdos; insmod ntfs; ls (hd1,msdos1)/
     - insmod part_gpt; insmod fat; ls (hd0,gpt2)/EFI/BOOT/
     - Note any BOOTX64.EFI, bootmgfw.efi, BCD, boot.sdi
5. Suspicious dirs & drivers (PCAT, CoreC2Firewallexemptions, *.sys, CORE_DXE)
   - Why: potential staging/backdoor location and kernel modules.
   - Common commands:
     - insmod part_msdos; insmod ntfs; ls (hd1,msdos1)/Backup/Windows/Boot/DVD/PCAT
     - ls (hd1,msdos1)/Windows/System32/drivers/

Grub (read-only) quick command pattern
- Device map:
  - ls
- Safe NTFS listing (primary pattern):
  - insmod part_msdos; insmod ntfs; ls (hd1,msdos1)/PATH/TO/CHECK
- EFI partition:
  - insmod part_gpt; insmod fat; ls (hd0,gpt2)/EFI/BOOT/
- If partition not found: try hd0/hd1/hd2 variants (ls (hd0); ls (hd1); ls (hd2))

Baseline compare approach (phone -> later on clean host)
- Capture screenshot(s) of grub output or copy lines into a secure note.
- When on clean host: image drive (ddrescue), mount read-only, produce baseline hashes:
  - find /mnt/evidence -type f -print0 | xargs -0 sha256sum > baseline_hashes.txt

Router & pre-boot containment (phone checklist)
1. Factory-reset router, disable Wi‑Fi radios, power down and unplug.  
2. Flush DNS on any live devices (only from a clean device if possible).  
3. Do not enable Internet on the target until you have a monitoring plan.  
4. Boot target offline (no Ethernet/Wi‑Fi). Keep phone/network separate.

Minimal BIOS checklist (quick toggles to inspect/set)
- Disable CSM (enable pure UEFI) if you will rely on UEFI secure boot workflows.  
- Secure Boot: enable (preferred) — note: if firmware-compromise suspected, enabling may fail; record state.  
- VT-x / virtualization: disable unless needed for controlled analysis.  
- Fast Boot: off.  
- USB boot: enabled (for live USB), but verify boot order and use a known-clean USB.  
- LAN controller/audio/unused ports: disable if you want minimal attack surface.  
- XMP / OC / Turbo / C‑states: revert to defaults (stability priority).  
- Save BIOS/UEFI config screenshot (phone) before changing.

Quick Ubuntu live minimal plan (if you boot clean USB)
- Create live USB on trusted machine; verify ISO checksum.
- Boot "Try Ubuntu" offline.
- Identify disks: sudo lsblk -o NAME,SIZE,FSTYPE,LABEL,MODEL
- If imaging: use gddrescue (see ddrescue commands in prior plan) to copy to external target.
- On image, run find + sha256sum for prioritized paths and share top hashes only.

Micro-loop operating rules (how we proceed interactively)
- You run 1 grub command I give, paste exact output here. I return the next single command and update this MD if you request.
- Keep each reply to raw grub output only (no commentary) to keep context minimal.

One-line risk summary (always present)
- Risk: any boot or write can execute attacker code and alter evidence; read-only grub ls is lowest-impact but not zero. You accept operational risk.

Notes about updates
- I will append/update this file with confirmed artifacts when you paste results and ask me to "update MD". Say "update MD with ID X" and I will add that line to this document.

End of compact update.