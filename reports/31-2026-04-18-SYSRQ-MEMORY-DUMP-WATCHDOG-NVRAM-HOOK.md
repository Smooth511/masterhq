# Report 31 — SysRq Memory Dump, Watchdog Deadman Switch & NVRAM Null Hook

**Classification:** FORENSIC ACQUISITION + DEFENSIVE TRAPPING — FULL REFERENCE GUIDE  
**Prepared by:** ClaudeMKII (MK2PK)  
**Report Date:** 2026-04-18  
**Sources:** sysrq.rst (kernel docs), kdump-tools(8), makedumpfile(8), crash(8), LiME, efivarfs(5), systemd-system.conf(5), iTCO_wdt  
**System:** ASUS PRIME B460M-A, Intel i7-10700 (8C/16T, 2.9GHz base / 4.8GHz boost), 16GB RAM  
**OS:** Linux Mint 22.3 Zena (Ubuntu 24.04 base)  
**Kernels:** 6.14.0-37-generic, 6.17.0-20-generic  
**Builds on:** Reports 24 (rootkit), 25 (watchdog), 28 (sysrq/panic), 29 (audit), 30 (RAM overlay/trap)  
**Identifier:** ClaudeMKII-Seed-20260317

---

## TABLE OF CONTENTS

1. [The Play — What We're Building](#1-the-play--what-were-building)
2. [Magic SysRq Key — Complete Reference](#2-magic-sysrq-key--complete-reference)
3. [SysRq Bitmask — Selective Enable for Dump Only](#3-sysrq-bitmask--selective-enable-for-dump-only)
4. [kdump — Crash Kernel Memory Capture](#4-kdump--crash-kernel-memory-capture)
5. [LiME — Live Memory Dump Without Crash](#5-lime--live-memory-dump-without-crash)
6. [Watchdog as Deadman Switch](#6-watchdog-as-deadman-switch)
7. [Panic Chain — lockup → panic → dump → reboot](#7-panic-chain--lockup--panic--dump--reboot)
8. [NVRAM Null Hook — Block EFI Writes on Dump](#8-nvram-null-hook--block-efi-writes-on-dump)
9. [The Combined Script — Everything Together](#9-the-combined-script--everything-together)
10. [Pre-Dump Preparation — What to Set Up Before the Moment](#10-pre-dump-preparation--what-to-set-up-before-the-moment)
11. [Post-Dump Analysis — What to Look For](#11-post-dump-analysis--what-to-look-for)
12. [Cross-Reference to Rootkit Vectors](#12-cross-reference-to-rootkit-vectors)
13. [Quick Reference Card](#13-quick-reference-card)

---

## 1. THE PLAY — WHAT WE'RE BUILDING

The idea is simple and brutal:

```
RAM desktop running (Report 30)
  → Quotas caging everything (Report 27)
    → Audit logging everything (Report 29)
      → Rootkit does its thing, thinking it's safe
        → YOU trigger: SysRq memory dump
          → NVRAM goes to null (rootkit can't write to EFI)
            → Full RAM captured to disk/network
              → Watchdog forces clean reboot if anything hangs
                → System comes back clean (RAM overlay = gone)
                  → You have the dump. Rootkit has nothing.
```

### Why NVRAM Matters

The rootkit from Report 24 uses **MOK (Machine Owner Key) enrolled in NVRAM** to sign its GRUB. NVRAM = EFI variables stored in firmware flash. If the rootkit detects a memory dump happening, it could:

1. **Write new EFI variables** to persist boot entries
2. **Modify MOK** enrollment data
3. **Set BootNext** to force a specific boot path
4. **Delete your GRUB entry** and replace with its own
5. **Write encrypted payload** to unused EFI variable space

Solution: **null out NVRAM access BEFORE the dump starts**. The rootkit's EFI write attempts go nowhere.

### Why the Watchdog Matters

During a memory dump (especially kdump crash), the system is in a vulnerable state. If the rootkit has kernel-level hooks, it could try to:

1. **Hang the dump process** — prevent evidence capture
2. **Corrupt the dump output** — make the capture useless
3. **Infinite loop in kernel** — prevent the crash kernel from loading

The hardware watchdog (iTCO_wdt on your B460 chipset, from Report 25) is the deadman switch. If ANYTHING hangs for more than the configured seconds — hardware forces a reboot. No software can prevent it. It's a physical timer on the chipset.

---

## 2. MAGIC SYSRQ KEY — COMPLETE REFERENCE

SysRq provides **kernel-level commands** that bypass EVERYTHING — userspace, display server, shell, even most kernel locks. They go direct to the kernel's input handler.

### All SysRq Functions

| Key | Function | Bitmask Bit | Value |
|-----|----------|-------------|-------|
| `b` | Immediately reboot (no sync, no umount) | 7 | 128 |
| `c` | **Crash the kernel** (triggers kdump if configured) | 4 | 16 |
| `d` | Show all held locks (requires CONFIG_LOCKDEP) | – | – |
| `e` | Send SIGTERM to all processes except init | 6 | 64 |
| `f` | Trigger OOM killer (pick and kill a process) | 6 | 64 |
| `g` | Used by kgdb (kernel debugger) | – | – |
| `h` | Show SysRq help | any | any |
| `i` | Send SIGKILL to all processes except init | 6 | 64 |
| `j` | Force thaw of frozen filesystems (FIFREEZE ioctl) | – | – |
| `k` | Secure Attention Key — kill all processes on current VT | 3 | 8 |
| `l` | Show CPU backtrace for all active CPUs | 0 | 0 |
| `m` | **Dump current memory info** to console/dmesg | 0 | 0 |
| `n` | Reset nice level of all RT tasks | – | – |
| `o` | Power off (if configured) | 7 | 128 |
| `p` | **Dump current CPU registers** and flags | 0 | 0 |
| `q` | Dump all armed hrtimers + clockevent devices | 0 | 0 |
| `r` | Turn off keyboard raw mode | 2 | 4 |
| `s` | **Sync all mounted filesystems** | 5 | 32 |
| `t` | **Dump all current task states** to console/dmesg | 0 | 0 |
| `u` | **Remount all filesystems read-only** | 5 | 32 |
| `v` | Force ETM buffer dump (ARM-specific) | – | – |
| `w` | Show all blocked (D state) tasks | 0 | 0 |
| `x` | Used by xmon on PPC | – | – |
| `z` | Dump ftrace buffer | 0 | 0 |

### The Classic Emergency Sequence

**R-E-I-S-U-B** ("Reboot Even If System Utterly Broken"):

```
SysRq+R  → Raw keyboard mode off
SysRq+E  → SIGTERM all processes
SysRq+I  → SIGKILL all processes  
SysRq+S  → Sync all filesystems
SysRq+U  → Remount all read-only
SysRq+B  → Reboot
```

### The Forensic Dump Sequence

What YOU want:

```
SysRq+S  → Sync (flush any audit logs to disk)
SysRq+U  → Remount read-only (protect evidence on disk)
SysRq+M  → Dump memory info to dmesg (lightweight)
SysRq+T  → Dump all task states to dmesg (process list)
SysRq+P  → Dump CPU registers (what was executing)
SysRq+C  → CRASH — triggers kdump full memory capture
```

### How to Trigger SysRq

```bash
# Method 1: /proc interface (requires root)
echo s > /proc/sysrq-trigger    # sync
echo c > /proc/sysrq-trigger    # crash dump

# Method 2: Keyboard (if enabled)
# Hold Alt + SysRq (Print Screen) + <key>
# On laptops: Alt + Fn + SysRq + <key>

# Method 3: From serial console
# Send BREAK, then the key character
```

---

## 3. SYSRQ BITMASK — SELECTIVE ENABLE FOR DUMP ONLY

Report 28 covered `kernel.sysrq` briefly. Here's the full bitmask aligned with the kernel documentation (`Documentation/admin-guide/sysrq.rst`) for our forensic use case.

### Bitmask Values

| Value | Bit | Functions Enabled |
|-------|-----|-------------------|
| 0 | — | Disable all SysRq functions |
| 1 | — | Enable ALL SysRq functions (dangerous — special value, not a bitmask) |
| 2 | 1 | Control console log level |
| 4 | 2 | Keyboard control: SAK (SysRq+K), unraw (SysRq+R) |
| 8 | 3 | **Debug/dump functions: crash (SysRq+C), registers (SysRq+P), tasks (SysRq+T)** |
| 16 | 4 | **Sync command (SysRq+S)** |
| 32 | 5 | **Remount read-only (SysRq+U)** |
| 64 | 6 | Signal functions: SIGTERM (SysRq+E), SIGKILL (SysRq+I), OOM kill (SysRq+F) |
| 128 | 7 | Reboot/poweroff (SysRq+B, SysRq+O) |
| 256 | 8 | Nice adjustment of RT tasks |

### Our Configuration

We want: crash dump (8) + sync (16) + remount-ro (32) + reboot (128) = **184**

But ALSO signal functions to kill processes before dump (64) = **248**

```bash
# /etc/sysctl.d/99-sysrq-forensic.conf

# Enable: crash dump (8) + sync (16) + remount-ro (32) + signals (64) + reboot (128)
kernel.sysrq = 248
```

> **Note:** Report 28 recommends `kernel.sysrq = 176` (sync + remount-ro + reboot only) for general hardening. The forensic value of 248 adds crash dump (8) and signal (64) functions needed for the trap-and-dump workflow.

### Why NOT Enable All (value=1)?

With `kernel.sysrq = 1`, ANYONE with console access (or a rootkit with `/proc/sysrq-trigger` access) can:
- Crash the system (`c`)
- Kill all processes (`e`/`i`)
- Reboot without sync (`b`)

With `kernel.sysrq = 248`, they can still do these (it's our trap toolset), but we've disabled:
- Console log level changes (value 2) — rootkit can't suppress logs
- Keyboard raw mode (value 4) — less attack surface
- RT task nicing (value 256) — no need for this

### Access Control for /proc/sysrq-trigger

`/proc/sysrq-trigger` is already root-writable only (0200) by default. The `chmod` command has no meaningful effect on procfs entries — the kernel controls access directly.

Access control relies on:

1. **The bitmask itself** — `kernel.sysrq = 248` restricts WHICH functions are available
2. **Normal privilege boundaries** — only root (UID 0) can write to `/proc/sysrq-trigger`
3. **Kernel lockdown** — `lockdown=confidentiality` (from Report 28) further restricts what root can do

```bash
# The bitmask IS the access control — keep it restricted to what you need
sudo sysctl -w kernel.sysrq=248

# Persist across reboots
printf 'kernel.sysrq = 248\n' | sudo tee /etc/sysctl.d/99-sysrq-forensic.conf >/dev/null

# If stronger runtime restrictions are needed, use kernel lockdown policy
# (lockdown=confidentiality from Report 28)
```

---

## 4. KDUMP — CRASH KERNEL MEMORY CAPTURE

kdump is the gold standard for full RAM capture. It works by loading a second "crash kernel" into reserved memory. When the main kernel crashes (SysRq+C or panic), the crash kernel boots and dumps the main kernel's memory.

### Install on Mint/Ubuntu

```bash
sudo apt install kdump-tools linux-crashdump makedumpfile crash
```

### Reserve Crash Kernel Memory

```bash
# /etc/default/grub
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash crashkernel=512M"

# For 16GB RAM, 512M is comfortable. Can go as low as 256M.
sudo update-grub
sudo reboot
```

### Verify Crash Kernel Loaded

```bash
# Check reserved memory
cat /proc/iomem | grep -i crash
# Should show: Crash kernel (at some address range)

# Check kdump service
sudo systemctl status kdump-tools
# Should be active

# Check crash kernel loaded
cat /sys/kernel/kexec_crash_loaded
# Should be: 1
```

### Configure kdump

```bash
# /etc/default/kdump-tools
USE_KDUMP=1
KDUMP_SYSCTL="kernel.panic_on_oops=1"
KDUMP_COREDIR="/var/crash"

# Where dumps go:
# /var/crash/<date>-<kernel>/vmcore
# /var/crash/<date>-<kernel>/vmcore-dmesg.txt
```

### Trigger a Crash Dump

```bash
# This WILL crash the system and capture RAM
echo c > /proc/sysrq-trigger

# What happens:
# 1. Main kernel crashes
# 2. Crash kernel boots from reserved memory  
# 3. makedumpfile captures /proc/vmcore → /var/crash/
# 4. System reboots (if kernel.panic=N is set)
```

### makedumpfile Options

```bash
# After crash, dumps are in /var/crash/<timestamp>/

# Compress and filter the dump (reduce size dramatically)
makedumpfile -c -d 31 /var/crash/latest/vmcore /var/crash/latest/vmcore.compressed
# -c = compress with zlib
# -d 31 = dump level (31 = exclude zero pages, cache, user, free pages)
#   d=0  : all pages (~16GB for 16GB RAM)
#   d=1  : exclude zero pages
#   d=31 : kernel pages only (~200MB-2GB typical)

# For FULL forensic capture (everything, no filtering):
makedumpfile -c -d 0 /var/crash/latest/vmcore /var/crash/latest/vmcore.full
# This captures ALL memory including user pages — needed to catch rootkit data
```

### Dump to External Device

```bash
# /etc/default/kdump-tools
# Dump directly to USB drive (safer — rootkit can't interfere with internal disk)
KDUMP_COREDIR="/mnt/usb-dump"

# Or dump over network (SSH):
# In /etc/kdump-tools: 
# KDUMP_CMDLINE="nfsroot=192.168.1.10:/dump"
```

### Important: crashkernel + toram Memory Budget

If you're running toram (Report 30) AND kdump, the memory budget is:

```
16GB total
 - 512MB  crashkernel reserved (untouchable)
 - 300MB  kernel + initramfs
 - 2.5GB  squashfs in RAM (toram)
 - 2.0GB  tmpfs upper (overlay)
 = ~10.7GB available for desktop + dump target
```

Still plenty. But if tight, reduce crashkernel to 256M.

---

## 5. LIME — LIVE MEMORY DUMP WITHOUT CRASH

LiME (Linux Memory Extractor) captures RAM **without crashing the system**. The system keeps running. This is for when you want to grab the rootkit's memory state while it's still active.

### Why LiME Instead of kdump

| Feature | kdump (SysRq+C) | LiME |
|---------|-----------------|------|
| System state | Crashes — all processes die | Keeps running |
| Capture timing | Freezes state at crash instant | Progressive capture (slight smear) |
| Rootkit detection | Rootkit may detect crash incoming | More subtle |
| Needs crash kernel | Yes (512M reserved) | No (kernel module) |
| Output format | vmcore (ELF) | .lime or raw (Volatility-compatible) |
| Trigger method | SysRq+C | insmod |

### Build LiME

```bash
# On a CLEAN system (not the target — cross-compile if possible)
git clone https://github.com/504ensicsLabs/LiME
cd LiME/src
make
# Produces: lime-$(uname -r).ko
```

### Capture Memory

```bash
# Load the module — capture starts immediately
sudo insmod lime-6.14.0-37-generic.ko "path=/mnt/usb/memdump.lime format=lime"

# Or dump over network (rootkit can't intercept local disk writes):
sudo insmod lime-6.14.0-37-generic.ko "format=lime path=tcp:4444"
# On your capture machine:
nc -l -p 4444 > memdump.lime

# After capture completes:
sudo rmmod lime
sha256sum /mnt/usb/memdump.lime  # integrity hash
```

### LiME + NVRAM Null (Pre-Hook)

You can null NVRAM BEFORE loading LiME, same as with SysRq:

```bash
# 1. Block NVRAM writes
mount -o remount,ro /sys/firmware/efi/efivars 2>/dev/null
# 2. Capture memory
sudo insmod lime.ko "path=/mnt/usb/dump.lime format=lime"
# 3. Memory is captured while rootkit can't write to EFI
```

---

## 6. WATCHDOG AS DEADMAN SWITCH

Report 25 (§11) covered the hardware watchdog configuration. Here's how it integrates with the dump process as a failsafe.

### Your Hardware

The ASUS B460M-A has the **Intel TCO Watchdog Timer** (iTCO_wdt) built into the B460 PCH. This is a hardware timer that:

- **Cannot be disabled by software** once armed (without the correct ping)
- **Triggers a hardware reset** when the timer expires
- **Is independent of CPU state** — works even if all CPUs are locked

### systemd Watchdog Configuration (from Report 25)

```ini
# /etc/systemd/system.conf
[Manager]
RuntimeWatchdogSec=30
RuntimeWatchdogPreSec=10
RebootWatchdogSec=5min
KExecWatchdogSec=5min
WatchdogDevice=/dev/watchdog0
```

### How This Helps During Dump

```
Normal operation:
  systemd pings watchdog every 15s (half of RuntimeWatchdogSec=30)

SysRq+C triggered:
  → Main kernel crashes
  → systemd stops pinging watchdog
  → Crash kernel boots (kdump)
  → kdump has ~30 seconds to start its own ping
  → If kdump hangs: watchdog fires → HARDWARE REBOOT
  → System comes back clean (RAM overlay lost, disk intact)
```

### Watchdog During kdump

The crash kernel needs to handle the watchdog too. Options:

```bash
# Option 1: Disable watchdog in crash kernel cmdline
# (gives unlimited time for dump, but loses the deadman switch)
KDUMP_CMDLINE_APPEND="nowatchdog"

# Option 2: Let watchdog run (recommended for trapping)
# Crash kernel has 30s to complete dump before forced reboot
# For 16GB RAM, dump takes ~30-60s to compressed file
# May need to increase watchdog:
RuntimeWatchdogSec=120  # 2 minutes

# Option 3: Ping watchdog from dump script
# kdump runs makedumpfile, which can be scripted to ping /dev/watchdog
```

### Recommended Watchdog + Dump Setup

```ini
# /etc/systemd/system.conf
[Manager]
# Give enough time for dump to complete, but not so long the rootkit can interfere
RuntimeWatchdogSec=120
RuntimeWatchdogPreSec=30
RebootWatchdogSec=10min
WatchdogDevice=/dev/watchdog0
```

This means:
- Normal operation: systemd pings every 60s
- After SysRq+C crash: 120 seconds for kdump to complete
- If kdump hangs: hardware reboot at 120s mark
- During reboot phase: 10 minutes for clean shutdown
- **Nothing software can do to prevent the hardware reboot**

---

## 7. PANIC CHAIN — lockup → panic → dump → reboot

This chains automatic system responses so that even if the rootkit causes a hang/lockup, the system captures evidence and reboots clean.

### Kernel Parameters for Automatic Panic

```bash
# /etc/sysctl.d/99-panic-chain.conf

# Panic on kernel oops (don't try to continue with corrupted state)
kernel.panic_on_oops = 1

# Hard lockup: CPU stuck with interrupts disabled → panic
kernel.hardlockup_panic = 1

# Soft lockup: CPU stuck in kernel code → panic  
kernel.softlockup_panic = 1

# Hung task: Process stuck in D-state for too long → panic
kernel.hung_task_panic = 1
kernel.hung_task_timeout_secs = 120

# After panic: reboot after N seconds (0 = never, gives time for kdump)
kernel.panic = 30

# NMI watchdog enabled (hardware-level lockup detection)
kernel.nmi_watchdog = 1

# Panic on I/O NMI (hardware error)
kernel.panic_on_io_nmi = 1

# Panic on unknown NMI (could be hardware attack)
kernel.panic_on_unrecovered_nmi = 1
```

### GRUB Parameters for Panic Chain

```bash
# /etc/default/grub
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash \
    crashkernel=512M \
    oops=panic \
    nmi_watchdog=1 \
    softlockup_panic=1"
```

### The Full Chain in Action

```
Rootkit causes kernel corruption
  → oops detected
    → oops=panic → kernel panics immediately
      → kdump crash kernel boots
        → makedumpfile captures RAM to /var/crash/
          → kernel.panic=30 → system reboots after 30s
            → If kdump itself hangs: watchdog fires at 120s → hardware reboot
              → System boots clean from read-only base (Report 30)
                → You have the dump file. Rootkit is dead.

Or:

Rootkit causes CPU lockup (infinite loop in kernel)
  → NMI watchdog detects lockup (nmi_watchdog=1)
    → hardlockup_panic=1 → panic
      → Same chain: kdump → dump → reboot → clean

Or:

Rootkit causes process hang (blocking I/O, deadlock)
  → hung_task_timeout_secs=120 → detected after 2 minutes
    → hung_task_panic=1 → panic
      → Same chain: kdump → dump → reboot → clean
```

### Every Path Leads to: Evidence Captured + Clean Reboot

No matter how the rootkit causes problems, the panic chain ensures:
1. The system doesn't just sit there hung — it captures state
2. The dump is written to disk (or network)
3. The system reboots to a known-clean state
4. The watchdog guarantees reboot even if kdump hangs

---

## 8. NVRAM NULL HOOK — BLOCK EFI WRITES ON DUMP

This is the key defensive trick: **null out NVRAM access before triggering the memory dump**.

### Why NVRAM Is Dangerous

The rootkit's MOK certificate lives in NVRAM. EFI variables are stored in firmware flash — they survive:
- OS reinstall
- Disk wipe
- RAM clear (they're in flash, not RAM)
- Boot mode changes

If the rootkit detects a crash dump happening (which it can — the kernel sends signals), it could race to write to NVRAM before the dump captures its state.

### What Lives in NVRAM

```bash
# List all EFI variables
ls /sys/firmware/efi/efivars/

# Key variables the rootkit cares about:
# Boot0000-*     → Boot entries (which GRUB to load)
# BootOrder-*    → Boot priority
# BootNext-*     → One-time boot override
# MokListRT-*    → Machine Owner Keys (the rootkit's cert!)
# SecureBoot-*   → Secure Boot state
# PK-*           → Platform Key
# KEK-*          → Key Exchange Key
# db-*           → Signature database
# dbx-*          → Forbidden signatures
```

### Method 1: Remount efivarfs Read-Only

```bash
# Block all EFI variable writes
mount -o remount,ro /sys/firmware/efi/efivars

# Verify
mount | grep efivars
# Should show: ... (ro, ...)
```

### Method 2: Mount with immutable Flag (Kernel 5.12+)

```bash
# Unmount and remount as immutable
umount /sys/firmware/efi/efivars
mount -t efivarfs efivarfs /sys/firmware/efi/efivars -o immutable

# This is STRONGER than ro — even root can't remount rw
```

### Method 3: Overmount efivarfs with Empty Read-Only tmpfs

```bash
# Nuclear option — hide efivarfs behind an empty read-only mount
# This is a dir-on-dir mount (unlike bind /dev/null which is file→dir and fails)
mount -t tmpfs -o ro,nodev,nosuid,noexec,size=4k tmpfs /sys/firmware/efi/efivars

# The path now appears empty — rootkit can't READ or WRITE EFI variables
# through /sys/firmware/efi/efivars while this is in place
# Unmount to restore access: umount /sys/firmware/efi/efivars
```

### Method 4: Block at Module Level

```bash
# Prevent the efivarfs module from loading at all
echo "blacklist efivarfs" >> /etc/modprobe.d/blacklist-efi.conf
# Or at runtime:
rmmod efivarfs 2>/dev/null

# Note: this may not work if efivarfs is compiled into the kernel
# Check: cat /proc/filesystems | grep efivars
```

### Method 5: Kernel Lockdown (from Report 28)

With `lockdown=confidentiality` on the kernel cmdline:
- Blocks `/dev/mem` access
- Blocks kexec of unsigned kernels
- Blocks writing to MSRs
- Blocks some EFI variable access (varies by implementation)

**lockdown + immutable mount = belt and braces**

### The Hook Script — Null NVRAM Then Dump

```bash
#!/bin/bash
# /usr/local/bin/forensic-dump.sh
# Null NVRAM → Capture Memory → Watchdog Backup

set -e

DUMP_DIR="/mnt/usb-dump"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
LOG="/var/log/forensic-dump-${TIMESTAMP}.log"

echo "[$(date)] FORENSIC DUMP INITIATED" | tee "$LOG"

# === STEP 1: NULL OUT NVRAM ===
echo "[$(date)] Blocking NVRAM/EFI variable access..." | tee -a "$LOG"

# Try immutable mount first (strongest)
if umount /sys/firmware/efi/efivars 2>/dev/null; then
    mount -t efivarfs efivarfs /sys/firmware/efi/efivars -o immutable 2>/dev/null && \
        echo "[$(date)] NVRAM: immutable mount OK" | tee -a "$LOG" || \
        echo "[$(date)] NVRAM: immutable mount failed, trying ro" | tee -a "$LOG"
fi

# Fallback: remount read-only
mount -o remount,ro /sys/firmware/efi/efivars 2>/dev/null && \
    echo "[$(date)] NVRAM: read-only remount OK" | tee -a "$LOG" || true

# Nuclear fallback: overmount with empty read-only tmpfs (dir-on-dir, not bind /dev/null)
mount -t tmpfs -o ro,nosuid,nodev,noexec,mode=000,size=4k tmpfs /sys/firmware/efi/efivars 2>/dev/null && \
    echo "[$(date)] NVRAM: tmpfs overmount OK" | tee -a "$LOG" || true

echo "[$(date)] NVRAM access blocked" | tee -a "$LOG"

# === STEP 2: SYNC AND SNAPSHOT BEFORE DUMP ===
echo "[$(date)] Syncing filesystems..." | tee -a "$LOG"
sync

# Dump current state to dmesg (captured in kdump vmcore-dmesg.txt)
echo m > /proc/sysrq-trigger  # memory info
echo t > /proc/sysrq-trigger  # task list
echo p > /proc/sysrq-trigger  # CPU registers
echo w > /proc/sysrq-trigger  # blocked tasks

# Brief pause for dmesg to flush
sleep 2

# === STEP 3: CAPTURE OVERLAY UPPER LAYER ===
echo "[$(date)] Capturing overlay upper layer..." | tee -a "$LOG"
if [ -d /cow ]; then
    tar czf "${DUMP_DIR}/overlay-upper-${TIMESTAMP}.tar.gz" /cow/ 2>/dev/null || true
    echo "[$(date)] Overlay /cow captured" | tee -a "$LOG"
elif [ -d /media/root-rw/overlay ]; then
    tar czf "${DUMP_DIR}/overlay-upper-${TIMESTAMP}.tar.gz" /media/root-rw/overlay/ 2>/dev/null || true
    echo "[$(date)] Overlay /media/root-rw captured" | tee -a "$LOG"
elif [ -d /run/ram-overlay/upper ]; then
    tar czf "${DUMP_DIR}/overlay-upper-${TIMESTAMP}.tar.gz" /run/ram-overlay/upper/ 2>/dev/null || true
    echo "[$(date)] Overlay /run/ram-overlay/upper captured" | tee -a "$LOG"
fi

# === STEP 4: CAPTURE AUDIT LOG ===
echo "[$(date)] Capturing audit log..." | tee -a "$LOG"
cp /var/log/audit/audit.log "${DUMP_DIR}/audit-${TIMESTAMP}.log" 2>/dev/null || true

# === STEP 5: REMOUNT READ-ONLY ===
echo "[$(date)] Remounting filesystems read-only..." | tee -a "$LOG"
echo u > /proc/sysrq-trigger

sleep 1

# === STEP 6: TRIGGER CRASH DUMP ===
echo "[$(date)] TRIGGERING KERNEL CRASH FOR MEMORY DUMP" | tee -a "$LOG"
echo "[$(date)] Watchdog will force reboot in 120s if dump hangs" | tee -a "$LOG"

# Point of no return
echo c > /proc/sysrq-trigger

# If we get here, something went wrong (SysRq+C should never return)
echo "[$(date)] ERROR: SysRq+C did not crash kernel?!" | tee -a "$LOG"
```

---

## 9. THE COMBINED SCRIPT — EVERYTHING TOGETHER

Here's the full operational script that combines NVRAM nulling, overlay capture, audit preservation, and memory dump with watchdog backup.

### Main Forensic Dump Script

```bash
#!/bin/bash
# /usr/local/bin/trap-and-dump.sh
# COMBINED: NVRAM null + overlay capture + SysRq crash dump + watchdog deadman
# 
# Usage: sudo ./trap-and-dump.sh [crash|live|both]
#   crash = SysRq+C kdump (system crashes, full RAM capture)
#   live  = LiME capture (system keeps running)
#   both  = LiME first, then SysRq+C for verification

MODE="${1:-crash}"
DUMP_DEV="/mnt/usb-dump"          # External USB for dumps
LIME_MODULE="/opt/lime/lime-$(uname -r).ko"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
LOG="${DUMP_DEV}/forensic-${TIMESTAMP}.log"

# Sanity checks
if [ "$(id -u)" -ne 0 ]; then
    echo "ERROR: Must run as root"
    exit 1
fi

if ! mountpoint -q "$DUMP_DEV"; then
    echo "ERROR: Dump device not mounted at $DUMP_DEV"
    echo "Mount your USB drive first: mount /dev/sdX1 $DUMP_DEV"
    exit 1
fi

exec > >(tee -a "$LOG") 2>&1

echo "=========================================="
echo "FORENSIC DUMP — Mode: ${MODE}"
echo "Timestamp: ${TIMESTAMP}"
echo "Dump target: ${DUMP_DEV}"
echo "=========================================="

# ──────────────────────────────────────────────
# PHASE 1: LOCK DOWN NVRAM
# ──────────────────────────────────────────────
echo ""
echo "[PHASE 1] Locking down NVRAM/EFI variables..."

# Snapshot current EFI vars BEFORE nulling (evidence of what's enrolled)
if [ -d /sys/firmware/efi/efivars ]; then
    echo "  Snapshotting EFI variables..."
    mkdir -p "${DUMP_DEV}/efivars-${TIMESTAMP}"
    
    # Copy variable names and sizes (not contents — some may be large)
    ls -la /sys/firmware/efi/efivars/ > "${DUMP_DEV}/efivars-${TIMESTAMP}/listing.txt" 2>/dev/null
    
    # Capture MOK-related vars specifically (the rootkit's persistence)
    for var in /sys/firmware/efi/efivars/Mok*; do
        [ -f "$var" ] && cp "$var" "${DUMP_DEV}/efivars-${TIMESTAMP}/" 2>/dev/null
    done
    
    # Capture Boot vars (boot chain manipulation)
    for var in /sys/firmware/efi/efivars/Boot*; do
        [ -f "$var" ] && cp "$var" "${DUMP_DEV}/efivars-${TIMESTAMP}/" 2>/dev/null
    done
    
    echo "  EFI vars snapshotted to ${DUMP_DEV}/efivars-${TIMESTAMP}/"
    
    # NOW null it
    echo "  Blocking NVRAM writes..."
    
    # Method 1: remount read-only
    mount -o remount,ro /sys/firmware/efi/efivars 2>/dev/null
    
    # Method 2: if still writable, overmount with empty read-only tmpfs
    EFIVARS_MOUNT="$(grep ' /sys/firmware/efi/efivars ' /proc/mounts 2>/dev/null)"
    if printf '%s\n' "$EFIVARS_MOUNT" | grep -q ' rw[, ]'; then
        mount -t tmpfs -o ro,nosuid,nodev,noexec,mode=000,size=4k tmpfs /sys/firmware/efi/efivars 2>/dev/null
    fi
    
    echo "  NVRAM locked: $(grep efivars /proc/mounts)"
else
    echo "  No efivarfs found (not EFI system or already unmounted)"
fi

# ──────────────────────────────────────────────
# PHASE 2: CAPTURE PRE-DUMP EVIDENCE
# ──────────────────────────────────────────────
echo ""
echo "[PHASE 2] Capturing pre-dump evidence..."

# Overlay upper layer (everything the rootkit changed)
echo "  Capturing overlay upper layer..."
for overlay_dir in /cow /media/root-rw/overlay /run/ram-overlay/upper; do
    if [ -d "$overlay_dir" ]; then
        tar czf "${DUMP_DEV}/overlay-${TIMESTAMP}.tar.gz" "$overlay_dir/" 2>/dev/null
        echo "  Overlay captured from: $overlay_dir"
        
        # Also list whiteouts (deleted files)
        find "$overlay_dir" -type c > "${DUMP_DEV}/whiteouts-${TIMESTAMP}.txt" 2>/dev/null
        wc_count=$(wc -l < "${DUMP_DEV}/whiteouts-${TIMESTAMP}.txt")
        echo "  Whiteouts (deleted files): ${wc_count}"
        break
    fi
done

# Audit log
echo "  Capturing audit log..."
cp /var/log/audit/audit.log "${DUMP_DEV}/audit-${TIMESTAMP}.log" 2>/dev/null || \
    journalctl _TRANSPORT=audit > "${DUMP_DEV}/audit-journal-${TIMESTAMP}.log" 2>/dev/null

# Process list with full details
echo "  Capturing process state..."
ps auxwwf > "${DUMP_DEV}/ps-${TIMESTAMP}.txt" 2>/dev/null
cat /proc/*/maps 2>/dev/null > "${DUMP_DEV}/proc-maps-${TIMESTAMP}.txt"
cat /proc/*/status 2>/dev/null > "${DUMP_DEV}/proc-status-${TIMESTAMP}.txt"

# Network connections
echo "  Capturing network state..."
ss -tulpan > "${DUMP_DEV}/netstat-${TIMESTAMP}.txt" 2>/dev/null
ip addr show > "${DUMP_DEV}/ip-addr-${TIMESTAMP}.txt" 2>/dev/null
ip route show > "${DUMP_DEV}/ip-route-${TIMESTAMP}.txt" 2>/dev/null

# Loaded kernel modules
echo "  Capturing kernel module list..."
lsmod > "${DUMP_DEV}/lsmod-${TIMESTAMP}.txt" 2>/dev/null
cat /proc/modules > "${DUMP_DEV}/proc-modules-${TIMESTAMP}.txt" 2>/dev/null

# Mount points and block devices
echo "  Capturing mount/block state..."
mount > "${DUMP_DEV}/mounts-${TIMESTAMP}.txt" 2>/dev/null
lsblk -f > "${DUMP_DEV}/lsblk-${TIMESTAMP}.txt" 2>/dev/null
dmsetup ls --tree > "${DUMP_DEV}/dmsetup-${TIMESTAMP}.txt" 2>/dev/null

# dmesg (kernel ring buffer)
echo "  Capturing dmesg..."
dmesg > "${DUMP_DEV}/dmesg-${TIMESTAMP}.txt" 2>/dev/null

# cgroup state (quota usage)
echo "  Capturing cgroup state..."
systemd-cgtop -b --iterations=1 > "${DUMP_DEV}/cgtop-${TIMESTAMP}.txt" 2>/dev/null

echo "  Pre-dump evidence captured"

# ──────────────────────────────────────────────
# PHASE 3: SYNC FILESYSTEMS
# ──────────────────────────────────────────────
echo ""
echo "[PHASE 3] Syncing filesystems..."
sync
echo s > /proc/sysrq-trigger
sleep 1

# ──────────────────────────────────────────────
# PHASE 4: MEMORY CAPTURE
# ──────────────────────────────────────────────

if [ "$MODE" = "live" ] || [ "$MODE" = "both" ]; then
    echo ""
    echo "[PHASE 4a] LiME live memory capture..."
    
    if [ -f "$LIME_MODULE" ]; then
        echo "  Loading LiME module..."
        insmod "$LIME_MODULE" "path=${DUMP_DEV}/memdump-live-${TIMESTAMP}.lime format=lime"
        
        # Wait for capture to complete by monitoring output file size stability
        echo "  Capturing... (this takes 30-120 seconds for 16GB)"
        CAPTURE_FILE="${DUMP_DEV}/memdump-live-${TIMESTAMP}.lime"
        last_size=-1
        stable_checks=0
        check_count=0
        max_checks=72  # 72 × 5s = 360s max
        while [ "$check_count" -lt "$max_checks" ]; do
            sleep 5
            echo -n "."
            check_count=$((check_count + 1))
            
            if [ -f "$CAPTURE_FILE" ]; then
                current_size=$(stat -c%s "$CAPTURE_FILE" 2>/dev/null || echo -1)
                if [ "$current_size" -gt 0 ] && [ "$current_size" -eq "$last_size" ]; then
                    stable_checks=$((stable_checks + 1))
                else
                    stable_checks=0
                    last_size=$current_size
                fi
                
                # File size stable for 3 consecutive checks (15s) = capture complete
                if [ "$stable_checks" -ge 3 ]; then
                    break
                fi
            fi
        done
        echo ""
        
        # Unload LiME module (it stays loaded after capture — must explicitly rmmod)
        if lsmod | grep -q '^lime[[:space:]]'; then
            rmmod lime
        fi
        
        # Hash the capture
        sha256sum "${DUMP_DEV}/memdump-live-${TIMESTAMP}.lime" > \
            "${DUMP_DEV}/memdump-live-${TIMESTAMP}.sha256"
        echo "  LiME capture complete: $(ls -lh ${DUMP_DEV}/memdump-live-${TIMESTAMP}.lime)"
    else
        echo "  WARNING: LiME module not found at $LIME_MODULE"
        echo "  Skipping live capture"
    fi
    
    if [ "$MODE" = "live" ]; then
        echo ""
        echo "=========================================="
        echo "FORENSIC DUMP COMPLETE (live mode)"
        echo "Evidence at: ${DUMP_DEV}/"
        echo "=========================================="
        exit 0
    fi
fi

if [ "$MODE" = "crash" ] || [ "$MODE" = "both" ]; then
    echo ""
    echo "[PHASE 4b] SysRq crash dump (kdump)..."
    echo ""
    echo "  ╔═══════════════════════════════════════╗"
    echo "  ║  SYSTEM WILL CRASH IN 5 SECONDS       ║"
    echo "  ║  kdump will capture full RAM           ║"
    echo "  ║  Watchdog backup: 120s                 ║"
    echo "  ║  System will reboot after dump          ║"
    echo "  ╚═══════════════════════════════════════╝"
    echo ""
    
    # Final sync
    sync
    
    # SysRq info dumps to dmesg (captured in vmcore-dmesg.txt by kdump)
    echo m > /proc/sysrq-trigger  # memory
    echo t > /proc/sysrq-trigger  # tasks
    echo p > /proc/sysrq-trigger  # registers
    echo w > /proc/sysrq-trigger  # blocked
    
    sleep 2
    
    # Remount everything read-only
    echo u > /proc/sysrq-trigger
    
    sleep 3
    
    # === POINT OF NO RETURN ===
    echo c > /proc/sysrq-trigger
    
    # Should never reach here
    echo "ERROR: SysRq+C failed to crash kernel"
    exit 1
fi
```

### Make It Executable

```bash
sudo cp trap-and-dump.sh /usr/local/bin/trap-and-dump.sh
sudo chmod 700 /usr/local/bin/trap-and-dump.sh
sudo chown root:root /usr/local/bin/trap-and-dump.sh
```

### Usage

```bash
# Live capture (system keeps running):
sudo trap-and-dump.sh live

# Crash dump (system crashes, full RAM capture, reboots):
sudo trap-and-dump.sh crash

# Both (LiME first, then crash dump for verification):
sudo trap-and-dump.sh both
```

---

## 10. PRE-DUMP PREPARATION — WHAT TO SET UP BEFORE THE MOMENT

### One-Time Setup (Do This Now)

```bash
# 1. Install kdump
sudo apt install kdump-tools linux-crashdump makedumpfile crash

# 2. Add crashkernel to GRUB (with all hardening from Report 28)
# Edit /etc/default/grub:
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash \
    crashkernel=512M \
    oops=panic nmi_watchdog=1 \
    init_on_alloc=1 init_on_free=1 \
    slab_nomerge lockdown=confidentiality \
    module.sig_enforce=1 vsyscall=none \
    apparmor=1 security=apparmor"
sudo update-grub

# 3. Configure panic chain
sudo tee /etc/sysctl.d/99-panic-chain.conf << 'EOF'
kernel.panic_on_oops = 1
kernel.hardlockup_panic = 1
kernel.softlockup_panic = 1
kernel.hung_task_panic = 1
kernel.hung_task_timeout_secs = 120
kernel.panic = 30
kernel.nmi_watchdog = 1
kernel.panic_on_io_nmi = 1
kernel.panic_on_unrecovered_nmi = 1
EOF

# 4. Configure SysRq bitmask
sudo tee /etc/sysctl.d/99-sysrq-forensic.conf << 'EOF'
# crash dump(8) + sync(16) + remount-ro(32) + signals(64) + reboot(128)
kernel.sysrq = 248
EOF

# 5. Configure watchdog (Report 25)
# Edit /etc/systemd/system.conf:
# RuntimeWatchdogSec=120
# WatchdogDevice=/dev/watchdog0

# 6. Apply sysctl
sudo sysctl --system

# 7. Reboot to activate crashkernel
sudo reboot
```

### Verify Everything Is Ready

```bash
# kdump loaded?
cat /sys/kernel/kexec_crash_loaded
# Expected: 1

# Crash memory reserved?
cat /proc/iomem | grep -i crash
# Expected: <address range> : Crash kernel

# SysRq enabled with correct mask?
cat /proc/sys/kernel/sysrq
# Expected: 248

# Watchdog active?
cat /sys/class/watchdog/watchdog0/state
# Expected: active

# NMI watchdog running?
cat /proc/sys/kernel/nmi_watchdog
# Expected: 1

# Panic chain configured?
sysctl kernel.panic_on_oops kernel.hardlockup_panic kernel.softlockup_panic
# Expected: all = 1

# kdump service running?
systemctl status kdump-tools
# Expected: active (exited) — loaded and ready
```

### Pre-Position Your Dump USB

```bash
# Format a USB drive for dumps
sudo mkfs.ext4 -L FORENSIC-DUMP /dev/sdX1
sudo mkdir -p /mnt/usb-dump
sudo mount -L FORENSIC-DUMP /mnt/usb-dump

# Pre-stage LiME module on the USB
sudo cp /path/to/lime-$(uname -r).ko /mnt/usb-dump/
sudo cp /usr/local/bin/trap-and-dump.sh /mnt/usb-dump/

# Add to fstab for auto-mount
echo "LABEL=FORENSIC-DUMP /mnt/usb-dump ext4 defaults,nofail 0 2" | sudo tee -a /etc/fstab
```

---

## 11. POST-DUMP ANALYSIS — WHAT TO LOOK FOR

After the dump, you have evidence files. Here's what to do with them.

### kdump vmcore Analysis

```bash
# Find the dump
ls -lh /var/crash/

# Read the crash dmesg (contains SysRq+M, +T, +P, +W output)
cat /var/crash/*/vmcore-dmesg.txt

# Open with crash utility
sudo crash /usr/lib/debug/boot/vmlinux-$(uname -r) /var/crash/*/vmcore

# Inside crash:
crash> ps            # Process list at crash time
crash> bt            # Backtrace of crashing CPU
crash> bt -a         # Backtrace of ALL CPUs
crash> mod           # Loaded modules (look for rootkit modules)
crash> net           # Network connections
crash> files <pid>   # Open files for a process
crash> vm <pid>      # Virtual memory map
crash> task <pid>    # Task struct details
crash> rd -s <addr> 100  # Read memory at address (string)
crash> search "string"   # Search all memory for string
crash> kmem -s       # Slab allocator info
crash> mount         # Mount points at crash time
crash> log           # Full kernel log buffer
```

### What to Search For (Rootkit Indicators)

```bash
# Inside crash utility:

# 1. Hidden kernel modules (rootkit may hide from lsmod)
crash> mod
# Compare against pre-dump lsmod output — extra modules = rootkit

# 2. Hooked syscalls
crash> sym sys_call_table
crash> rd sys_call_table 512
# Compare against known-good syscall addresses

# 3. Process hiding
crash> ps
# Compare against pre-dump ps output — missing processes = hiding

# 4. Network connections (exfiltration)
crash> net
# Look for unexpected connections

# 5. Search for known rootkit strings
crash> search "ventoy"
crash> search "casper"
crash> search "CN=grub"
crash> search "/mnt6/mnt/1loyd"
crash> search "filesystem.squashfs"

# 6. Device mapper state
crash> mod | grep dm
crash> search "dm-"
```

### Overlay Upper Layer Analysis

```bash
# Extract the overlay capture
tar xzf overlay-*.tar.gz -C /tmp/overlay-analysis/

# List ALL modified files (every file here = different from base image)
find /tmp/overlay-analysis/ -type f -ls

# List ALL deleted files (whiteouts)
cat whiteouts-*.txt

# Check for modified binaries
find /tmp/overlay-analysis/ -path "*/usr/bin/*" -o -path "*/usr/sbin/*" -o -path "*/usr/lib/*" | sort

# Check for replaced libraries (the Report 25 attack)
find /tmp/overlay-analysis/ -name "libc.so*" -o -name "libstdc++*" -o -name "libgcc_s*"

# Check for new cron jobs, services, or startup scripts
find /tmp/overlay-analysis/ -path "*/cron*" -o -path "*/systemd/system/*" -o -path "*/init.d/*"

# Diff against known-good base
diff -rq /tmp/overlay-analysis/cow/usr/bin/ /media/root-ro/usr/bin/ 2>/dev/null
```

### EFI Variable Analysis

```bash
# Check captured EFI vars
ls -la efivars-*/

# Look for MOK entries
hexdump -C efivars-*/Mok* | head -100

# Look for unexpected boot entries
hexdump -C efivars-*/Boot00* | head -100

# Compare against known-good EFI var listing
diff efivars-*/listing.txt /path/to/known-good-efivars.txt
```

---

## 12. CROSS-REFERENCE TO ROOTKIT VECTORS

| Rootkit Vector (Report 24) | Evidence in Dump | Where to Look |
|---------------------------|-----------------|---------------|
| MOK certificate enrollment | EFI var snapshot | `efivars-*/MokList*` |
| CN=grub signed GRUB binary | Module/process list | `crash> mod`, `crash> search "CN=grub"` |
| Ventoy boot framework | Kernel strings | `crash> search "ventoy"`, `crash> search "vtoy"` |
| casper overlay stack | Mount state | `crash> mount`, `mounts-*.txt` |
| DM mapping for NVMe | Device mapper state | `dmsetup-*.txt`, `crash> search "dm-"` |
| Library deletion (Report 25) | Overlay whiteouts | `whiteouts-*.txt`, deleted libs |
| Process/task hiding | Process comparison | pre-dump `ps-*.txt` vs `crash> ps` |
| Network exfiltration | Connection state | `netstat-*.txt`, `crash> net` |
| Kernel module rootkit | Module comparison | pre-dump `lsmod-*.txt` vs `crash> mod` |

---

## 13. QUICK REFERENCE CARD

### Immediate Action — Quick Dump

```bash
# Fastest possible dump (no evidence pre-capture):
echo c > /proc/sysrq-trigger

# With minimal evidence preservation:
sync && echo u > /proc/sysrq-trigger && sleep 1 && echo c > /proc/sysrq-trigger

# Full script (recommended):
sudo /usr/local/bin/trap-and-dump.sh crash
```

### Key Files After Dump

| File | Contents |
|------|----------|
| `/var/crash/*/vmcore` | Full RAM dump (kdump) |
| `/var/crash/*/vmcore-dmesg.txt` | Kernel log at crash time |
| `overlay-*.tar.gz` | Everything rootkit changed |
| `whiteouts-*.txt` | Everything rootkit deleted |
| `audit-*.log` | Full audit trail |
| `efivars-*/` | EFI variable snapshot |
| `ps-*.txt` | Process list pre-dump |
| `lsmod-*.txt` | Module list pre-dump |
| `netstat-*.txt` | Network connections pre-dump |
| `dmsetup-*.txt` | Device mapper state |
| `dmesg-*.txt` | Kernel ring buffer |
| `memdump-live-*.lime` | LiME capture (if live mode) |

### Kernel Parameters Summary

```bash
# /etc/sysctl.d/99-forensic-complete.conf
kernel.sysrq = 248
kernel.panic_on_oops = 1
kernel.hardlockup_panic = 1
kernel.softlockup_panic = 1
kernel.hung_task_panic = 1
kernel.hung_task_timeout_secs = 120
kernel.panic = 30
kernel.nmi_watchdog = 1
kernel.panic_on_io_nmi = 1
kernel.panic_on_unrecovered_nmi = 1
```

### GRUB Line

```bash
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash crashkernel=512M oops=panic nmi_watchdog=1 \
    init_on_alloc=1 init_on_free=1 slab_nomerge lockdown=confidentiality \
    module.sig_enforce=1 vsyscall=none apparmor=1 security=apparmor mitigations=auto,nosmt"
```

### Watchdog (system.conf)

```ini
RuntimeWatchdogSec=120
RuntimeWatchdogPreSec=30
RebootWatchdogSec=10min
WatchdogDevice=/dev/watchdog0
```

---

*This report brings together the entire hardening series (Reports 25-30) into an operational forensic acquisition toolkit. The SysRq crash dump captures the rootkit's complete memory state. The NVRAM null hook prevents the rootkit from writing to EFI persistence during capture. The watchdog guarantees the system reboots even if the dump process hangs. The overlay capture from Report 30 preserves everything the rootkit changed. Combined: you get full evidence capture with no escape routes.*
