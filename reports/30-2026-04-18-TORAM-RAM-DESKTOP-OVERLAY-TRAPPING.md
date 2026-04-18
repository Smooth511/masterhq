# Report 30 — Running the Entire Desktop from RAM: toram, overlayroot & Defensive Trapping

**Classification:** SYSTEM HARDENING + FORENSIC TRAPPING — FULL REFERENCE GUIDE  
**Prepared by:** ClaudeMKII (MK2PK)  
**Report Date:** 2026-04-18  
**Sources:** casper(7), overlayroot(8), systemd-volatile-root.service(8), kernel overlayfs docs, dm-verity docs  
**System:** ASUS PRIME B460M-A, Intel i7-10700 (8C/16T, 2.9GHz base / 4.8GHz boost), 16GB RAM  
**OS:** Linux Mint 22.3 Zena (Ubuntu 24.04 base)  
**Kernels:** 6.14.0-37-generic, 6.17.0-20-generic  
**Builds on:** Reports 24 (rootkit boot chain), 25-29 (systemd + kernel hardening series)  
**Identifier:** ClaudeMKII-Seed-20260317

---

## TABLE OF CONTENTS

1. [Why Run from RAM](#1-why-run-from-ram)
2. [How the Rootkit Already Does This](#2-how-the-rootkit-already-does-this)
3. [Method 1 — casper `toram` Boot Parameter](#3-method-1--casper-toram-boot-parameter)
4. [Method 2 — `overlayroot` (Installed System)](#4-method-2--overlayroot-installed-system)
5. [Method 3 — `systemd.volatile=overlay`](#5-method-3--systemdvolatileoverlay)
6. [Method 4 — Manual tmpfs + overlayfs in initramfs](#6-method-4--manual-tmpfs--overlayfs-in-initramfs)
7. [Memory Budget — What 16GB Gets You](#7-memory-budget--what-16gb-gets-you)
8. [Swap: Kill It or Encrypt It](#8-swap-kill-it-or-encrypt-it)
9. [The Trap — Turning RAM Operation into a Cage](#9-the-trap--turning-ram-operation-into-a-cage)
10. [Quota Enforcement Inside the RAM Environment](#10-quota-enforcement-inside-the-ram-environment)
11. [Audit Rules for Overlay Detection](#11-audit-rules-for-overlay-detection)
12. [dm-verity — Tamper-Proof Base Layer](#12-dm-verity--tamper-proof-base-layer)
13. [Complete Defensive Configuration](#13-complete-defensive-configuration)
14. [Cross-Reference to Rootkit Attack Chain](#14-cross-reference-to-rootkit-attack-chain)
15. [Quick Reference Card](#15-quick-reference-card)

---

## 1. WHY RUN FROM RAM

Running the entire desktop from RAM means **every file, every binary, every library** lives in volatile memory. When the machine powers off, everything vanishes. No persistence. No rootkit survival between boots.

### What This Gives You

| Property | Disk-Based System | RAM-Based System |
|----------|-------------------|------------------|
| **Persistence** | Everything survives reboot | Nothing survives reboot |
| **Rootkit survival** | Rootkit persists on disk | Rootkit dies at poweroff |
| **Disk tampering** | Attacker modifies disk binaries | Disk is read-only or unmounted |
| **Speed** | Limited by NVMe/SSD I/O | RAM speed (~50GB/s DDR4) |
| **Forensic state** | Attacker can modify evidence | Evidence preserved on read-only disk |
| **Attack surface** | Full disk write access | Writes go to tmpfs only |

### The Key Insight

The rootkit documented in Report 24 **already runs from RAM** via casper live boot + Ventoy. It uses the same technique defensively — the rootkit's own binaries are in a squashfs that's overlay-mounted. The attacker chose this architecture because it works.

**You can use the exact same architecture, but under YOUR control.**

---

## 2. HOW THE ROOTKIT ALREADY DOES THIS

From Report 24, the rootkit's boot chain:

```
EFI → CN=grub signed GRUB → stock Ventoy (NVMe) → DM mapping → casper live → overlayfs
```

What this means in RAM terms:

1. **squashfs** (`filesystem.squashfs`) contains the compressed OS image (~2-4GB compressed)
2. **casper** mounts squashfs as **read-only lower layer**
3. **overlayfs** creates a **writable upper layer** backed by tmpfs (RAM)
4. Merged view = functional desktop where writes go to RAM, reads come from squashfs

The rootkit's `/cow` directory (Copy-On-Write) IS the RAM-based upper layer. Every modification the rootkit makes to system files exists only in `/cow` on tmpfs.

### What the Rootkit's Overlay Stack Looks Like

```
/  (merged view — what processes see)
├── lowerdir = /rofs  (read-only squashfs — the base OS image)
├── upperdir = /cow   (tmpfs — all modifications live here)
└── workdir  = /cow   (overlayfs work directory)
```

**This is literally the architecture you want to copy** — but with your own squashfs, your own GRUB, your own audit hooks watching the upper layer.

---

## 3. METHOD 1 — CASPER `toram` BOOT PARAMETER

### What `toram` Does

The `toram` boot parameter tells casper to **copy the entire squashfs image from disk into RAM** before mounting it. After the copy, the boot media (USB/NVMe/DVD) is no longer needed.

### How It Works Internally

Casper's initramfs contains `/scripts/casper-bottom/25copytoram`:

```
Boot → initramfs → casper scripts → detect toram → copy squashfs to /dev/shm → mount from RAM
```

Step by step:

1. Kernel boots, unpacks initramfs
2. Casper scripts run from `/scripts/casper`
3. `25copytoram` checks kernel cmdline for `toram`
4. If present: `cp /cdrom/casper/filesystem.squashfs /dev/shm/filesystem.squashfs`
5. Loop-mounts the **RAM copy** as the read-only lower layer
6. overlayfs upper layer (also tmpfs) goes on top
7. Boot media can be physically removed

### GRUB Configuration for toram

```bash
# /boot/grub/grub.cfg (or GRUB menu entry)
menuentry "Linux Mint — Full RAM Mode" {
    linux /casper/vmlinuz boot=casper toram quiet splash
    initrd /casper/initrd.lz
}
```

### All Casper Boot Parameters (Security-Relevant)

| Parameter | Effect |
|-----------|--------|
| `toram` | Copy entire squashfs to RAM |
| `boot=casper` | Use casper live boot system |
| `nopersistent` | Disable persistent storage (even if casper-rw exists) |
| `union=overlay` | Force overlayfs (not aufs) — default on modern Ubuntu |
| `ip=` | Network config (PXE/netboot) |
| `fetch=URL` | Fetch squashfs from network URL |
| `live-media-path=PATH` | Custom path to live files |
| `live-media=DEVICE` | Force specific boot device |
| `layerfs-path=FILE` | Additional squashfs layers (Ubuntu 22.04+) |
| `debug` | Verbose casper output |

### toram + Security Hardening (Combined GRUB Line)

From Report 28's kernel cmdline hardening, combined with toram:

```bash
linux /casper/vmlinuz boot=casper toram nopersistent \
    quiet splash \
    init_on_alloc=1 init_on_free=1 \
    slab_nomerge page_poison=1 \
    lockdown=confidentiality \
    module.sig_enforce=1 \
    vsyscall=none \
    randomize_kstack_offset=on \
    debugfs=off \
    lsm=landlock,lockdown,yama,apparmor,bpf \
    apparmor=1 security=apparmor \
    mitigations=auto,nosmt
```

### Memory Impact of toram

| Component | Typical Size | Notes |
|-----------|-------------|-------|
| filesystem.squashfs (compressed) | 2.0–4.5 GB | Copied to RAM as-is |
| squashfs decompression cache | 0.5–1.0 GB | Kernel manages this |
| overlayfs upper (tmpfs /cow) | 0.5–2.0 GB | Grows with modifications |
| Kernel + initramfs | 0.1–0.3 GB | Fixed |
| **Total base** | **~3–8 GB** | Before user applications |

With 16GB RAM: you'll have **8-13GB free** for applications after toram boot. Plenty for a desktop.

---

## 4. METHOD 2 — `overlayroot` (INSTALLED SYSTEM)

### What overlayroot Does

`overlayroot` is an Ubuntu package that converts a **normal installed system** into a RAM-overlay system. Your real root filesystem becomes read-only; all writes go to a tmpfs overlay.

This is different from casper/toram — it works on a **regular installed system**, not a live boot.

### Installation

```bash
sudo apt install overlayroot
```

### Configuration — `/etc/overlayroot.conf`

```bash
# /etc/overlayroot.conf

# === RAM OVERLAY (ephemeral — all changes lost at reboot) ===
overlayroot="tmpfs"

# === ALTERNATIVE: Specify tmpfs size ===
# overlayroot="tmpfs:swap=1,recurse=0"

# === DISABLED (normal persistent root) ===
# overlayroot=""
```

### How It Works

After reboot with `overlayroot="tmpfs"`:

```
/  (merged view)
├── lowerdir = /media/root-ro  (your real root, mounted read-only)
├── upperdir = /media/root-rw/overlay  (tmpfs — RAM)
└── workdir  = /media/root-rw/overlay-workdir
```

### Key Properties

| Property | Value |
|----------|-------|
| **Real root** | Read-only, untouched |
| **All writes** | Go to tmpfs (RAM) |
| **Reboot** | System returns to exact installed state |
| **Disk access** | Read-only — rootkit cannot modify disk binaries |
| **Performance** | Writes are RAM-speed; reads may still come from disk |

### Temporarily Disabling overlayroot (for Updates)

```bash
# Get a shell with the real writable root
sudo overlayroot-chroot

# Inside this chroot, you can:
apt update && apt upgrade
# Then exit and reboot — overlay resumes
exit
```

### overlayroot vs toram

| Feature | toram | overlayroot |
|---------|-------|-------------|
| System type | Live boot (casper) | Installed system |
| Base image | squashfs on media | Real root partition |
| Base in RAM? | Yes (entire squashfs copied) | No (reads from disk) |
| Write layer | tmpfs | tmpfs |
| Remove boot media? | Yes | N/A (disk-based) |
| Speed | All RAM | Reads from disk, writes to RAM |
| Updates | Replace squashfs | overlayroot-chroot |

### Why overlayroot Matters for You

If you install Linux Mint normally and enable `overlayroot="tmpfs"`:
- Your installed root **cannot be modified** by anything (rootkit included)
- All runtime changes (including anything the rootkit does) are **in RAM only**
- On reboot, the rootkit's changes **vanish**
- Your real system binaries remain **pristine on disk**

The rootkit would need to modify the boot chain itself (GRUB/EFI/initramfs) to survive — which is exactly what Reports 28 and 29's hardening prevents.

---

## 5. METHOD 3 — `systemd.volatile=overlay`

### What It Does

systemd (v239+) has built-in support for volatile root. Adding `systemd.volatile=overlay` to the kernel command line makes systemd:

1. Remount root as **read-only**
2. Create a **tmpfs overlay** on top
3. All writes go to RAM

### Boot Parameter Options

| Parameter | Effect |
|-----------|--------|
| `systemd.volatile=no` | Normal persistent root (default) |
| `systemd.volatile=overlay` | Root is disk read-only + tmpfs writable overlay |
| `systemd.volatile=yes` | Root is PURE tmpfs — nothing from disk (blank system) |
| `systemd.volatile=state` | Only `/var` is tmpfs, rest is persistent |

### GRUB Configuration

```bash
# /etc/default/grub
GRUB_CMDLINE_LINUX="systemd.volatile=overlay"

# Then:
sudo update-grub
```

### Combined with Hardening (Full GRUB Line)

```bash
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash systemd.volatile=overlay \
    init_on_alloc=1 init_on_free=1 \
    slab_nomerge lockdown=confidentiality \
    module.sig_enforce=1 vsyscall=none \
    apparmor=1 security=apparmor \
    mitigations=auto,nosmt"
```

### systemd.volatile vs overlayroot

| Feature | systemd.volatile=overlay | overlayroot |
|---------|-------------------------|-------------|
| Provider | systemd (built-in) | overlayroot package |
| Configuration | Kernel cmdline | /etc/overlayroot.conf |
| Update mechanism | Remove boot param, reboot | overlayroot-chroot |
| Maturity | Newer (systemd 239+) | Mature (Ubuntu) |
| Flexibility | 4 modes (no/yes/overlay/state) | tmpfs or device |
| Distribution support | Any systemd distro | Ubuntu/Mint |

### Best Choice for Your System

Linux Mint 22.3 Zena with systemd: **both work**. `overlayroot` is more mature and battle-tested on Ubuntu-based systems. `systemd.volatile=overlay` is simpler (just a boot param) but slightly less configurable.

**Recommendation:** Start with `overlayroot="tmpfs"` for the installed system, or `toram` if running live.

---

## 6. METHOD 4 — MANUAL TMPFS + OVERLAYFS IN INITRAMFS

For maximum control, you can build your own initramfs hook that creates the overlay stack manually. This is what the rootkit essentially does — and what you'd do for a custom forensic trapping environment.

### Custom initramfs Script — `/etc/initramfs-tools/scripts/init-bottom/ram-overlay`

```bash
#!/bin/sh
# /etc/initramfs-tools/scripts/init-bottom/ram-overlay
# Custom RAM overlay — forces entire root to tmpfs overlay

PREREQ=""
prereqs() { echo "$PREREQ"; }
case $1 in prereqs) prereqs; exit 0;; esac

# Only activate if ram-overlay is on kernel cmdline
grep -q "ram-overlay" /proc/cmdline || exit 0

# Create tmpfs for upper layer
mkdir -p /run/ram-overlay/upper /run/ram-overlay/work

# Size the tmpfs — use 75% of available RAM
mount -t tmpfs -o size=75%,mode=0755 tmpfs /run/ram-overlay

mkdir -p /run/ram-overlay/upper /run/ram-overlay/work

# Move the real root to a read-only mount point
mkdir -p /run/ram-overlay/lower
mount --move ${rootmnt} /run/ram-overlay/lower
mount -o remount,ro /run/ram-overlay/lower

# Create the overlay
mount -t overlay overlay \
    -o lowerdir=/run/ram-overlay/lower,upperdir=/run/ram-overlay/upper,workdir=/run/ram-overlay/work \
    ${rootmnt}

# Bind the lower (read-only real root) so we can inspect it later
mkdir -p ${rootmnt}/media/root-ro
mount --bind /run/ram-overlay/lower ${rootmnt}/media/root-ro
```

### Make It Executable and Rebuild initramfs

```bash
sudo chmod +x /etc/initramfs-tools/scripts/init-bottom/ram-overlay
sudo update-initramfs -u
```

### Boot Parameter

```bash
# Add to GRUB:
GRUB_CMDLINE_LINUX="ram-overlay"
sudo update-grub
```

### Why Manual Is Useful

- **Full control** over tmpfs size, mount options, overlay structure
- **Access to read-only lower** at `/media/root-ro` for live comparison
- **Custom forensic hooks** can be added to the same initramfs script
- **Audit the upper layer** at any time: `ls /run/ram-overlay/upper` shows ONLY what changed

---

## 7. MEMORY BUDGET — WHAT 16GB GETS YOU

Your ASUS system has 16GB DDR4. Here's the realistic memory budget:

### Scenario A: toram (Live Boot, Full RAM)

| Component | Size | Notes |
|-----------|------|-------|
| Kernel + initramfs | 300 MB | Fixed |
| filesystem.squashfs in RAM | 2.5–4.0 GB | Mint squashfs ~2.5GB |
| squashfs decompression | 0.5–1.0 GB | Kernel cache |
| overlayfs /cow (upper) | 0.5–2.0 GB | Grows with changes |
| **Subtotal: OS** | **~4–7 GB** | |
| **Available for apps** | **~9–12 GB** | |

### Scenario B: overlayroot (Installed, Reads from Disk)

| Component | Size | Notes |
|-----------|------|-------|
| Kernel + initramfs | 300 MB | Fixed |
| overlayfs upper (tmpfs) | 0.5–2.0 GB | Only modified files |
| Page cache (disk reads) | 2–6 GB | Kernel manages automatically |
| **Subtotal: OS** | **~3–8 GB** | |
| **Available for apps** | **~8–13 GB** | |

### Scenario C: systemd.volatile=overlay

Similar to overlayroot — reads from disk, writes to tmpfs. Memory budget matches Scenario B.

### Application Memory (Typical Desktop)

| Application | Typical RAM | Notes |
|-------------|------------|-------|
| Cinnamon desktop | 400–800 MB | Mint default DE |
| Firefox (10 tabs) | 500 MB–2 GB | Varies wildly |
| Terminal (multiple) | 50–200 MB | |
| File manager | 100–300 MB | |
| System services | 300–600 MB | systemd, NetworkManager, etc |
| **Typical total** | **~1.5–4 GB** | |

### Verdict

16GB is **more than enough** for any of these methods, including toram with a full Mint desktop. You'll have 8+ GB headroom in the worst case.

---

## 8. SWAP: KILL IT OR ENCRYPT IT

When running from RAM, swap is a **security problem**. Any data written to swap hits the disk and can persist.

### Option 1: Disable Swap Entirely

```bash
# Immediate (until reboot)
sudo swapoff -a

# Permanent
sudo sed -i '/swap/d' /etc/fstab
# Or comment out:
sudo sed -i 's/^.*swap/#&/' /etc/fstab
```

### Option 2: Encrypted Swap (If You Need It)

```bash
# /etc/crypttab
swap    /dev/sdX2    /dev/urandom    swap,cipher=aes-xts-plain64,size=256
```

This creates a **new random key at every boot** — swap contents from previous boot are unrecoverable.

### Option 3: zram (Compressed RAM Swap)

```bash
# Install zram-config (Ubuntu/Mint)
sudo apt install zram-config

# Or manually:
modprobe zram num_devices=1
echo lz4 > /sys/block/zram0/comp_algorithm
echo 4G > /sys/block/zram0/disksize
mkswap /dev/zram0
swapon /dev/zram0
```

zram never touches disk — it compresses memory pages within RAM itself. Best of both worlds: more effective memory without disk exposure.

### Recommendation for Your System

**zram + no disk swap.** You get the equivalent of ~20-24GB usable memory from your 16GB physical RAM (lz4 compression typically achieves 2:1 to 3:1), with zero disk writes.

```bash
# /etc/default/zramswap (if available)
ALGO=lz4
PERCENT=50    # Use 50% of RAM for zram = 8GB compressed ≈ 16-24GB effective
PRIORITY=100
```

---

## 9. THE TRAP — TURNING RAM OPERATION INTO A CAGE

This is the key section. You mentioned trapping the rootkit "like I do windows" — here's how to make the RAM environment into a monitored cage.

### The Concept

```
┌─────────────────────────────────────────────────────────┐
│                    YOUR CONTROL LAYER                    │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │            VISIBLE DESKTOP (overlay)             │    │
│  │                                                  │    │
│  │  Everything the rootkit sees and interacts with  │    │
│  │  is inside this cage.                           │    │
│  │                                                  │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────────┐    │    │
│  │  │ CPU Quota│ │ Mem Quota│ │ I/O Quota    │    │    │
│  │  │ per svc  │ │ per svc  │ │ per svc      │    │    │
│  │  └──────────┘ └──────────┘ └──────────────┘    │    │
│  │                                                  │    │
│  └─────────────────────────────────────────────────┘    │
│                         │                               │
│  ┌──────────────────────▼──────────────────────────┐    │
│  │              AUDIT LAYER (auditd)                │    │
│  │  Watches: /cow, /dev, module_load, execve,      │    │
│  │  mount, ptrace, device_mapper, /boot             │    │
│  │  Logs to: remote syslog OR encrypted partition   │    │
│  └─────────────────────────────────────────────────┘    │
│                         │                               │
│  ┌──────────────────────▼──────────────────────────┐    │
│  │           READ-ONLY BASE (squashfs/disk)         │    │
│  │  dm-verity protected. Cannot be modified.        │    │
│  │  Any read that fails hash = ALERT.               │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### How This Traps the Rootkit

1. **The rootkit thinks it's running normally** — it sees a writable filesystem, can modify files, can run processes
2. **Every modification lands in the tmpfs upper layer** — you can inspect `/run/ram-overlay/upper` (or `/cow`) at any time to see EXACTLY what changed
3. **Every process is resource-caged** — cgroup quotas from Report 27 limit CPU/memory/IO per service
4. **Every syscall is logged** — auditd rules from Report 29 catch execve, module loads, device access, etc.
5. **The base system is cryptographically verified** — dm-verity catches any attempt to tamper with the read-only lower layer
6. **Nothing survives reboot** — power off, come back to clean system

### The Windows Parallel

What you do on Windows (setting quotas and monitoring to catch the rootkit's activity) translates directly:

| Windows Technique | Linux RAM Equivalent |
|-------------------|---------------------|
| Resource Monitor | `systemd-cgtop` + cgroup quotas (Report 27) |
| Process Explorer | `auditd` execve tracking (Report 29) |
| Disk quota | `tmpfs size=` limit on upper layer |
| Event log | auditd → remote syslog |
| SFC /scannow | dm-verity hash verification (continuous) |
| Task Manager limits | `CPUQuota=`, `MemoryMax=` per service |

---

## 10. QUOTA ENFORCEMENT INSIDE THE RAM ENVIRONMENT

From Report 27's cgroup controls, here's how to set up resource quotas specifically for the RAM environment.

### tmpfs Size Quota (Limit Total Writes)

The overlayfs upper layer is on tmpfs. You can cap its size:

```bash
# Limit upper layer to 2GB — rootkit can only write 2GB total
mount -t tmpfs -o size=2G,mode=0755 tmpfs /run/ram-overlay

# Or for overlayroot, edit /etc/overlayroot.conf:
overlayroot="tmpfs:swap=0,recurse=0"
# Then override mount in /etc/fstab or systemd mount unit with size=
```

When the 2GB fills up: **all writes fail with ENOSPC**. The rootkit can't write anything else. You get an alert.

### Per-Service Resource Quotas

Create a hardened slice for all system services:

```ini
# /etc/systemd/system/system-hardened.slice
[Slice]
CPUQuota=200%
MemoryMax=4G
MemoryHigh=3G
TasksMax=512
IOReadBandwidthMax=/dev/nvme0n1 100M
IOWriteBandwidthMax=/dev/nvme0n1 50M
```

Then assign services to the slice:

```ini
# /etc/systemd/system/some-service.service.d/hardened.conf
[Service]
Slice=system-hardened.slice
CPUQuota=20%
MemoryMax=512M
TasksMax=32
```

### Anomaly Detection via Quotas

```bash
# Watch for services hitting their limits
systemd-cgtop --recursive --delay=2

# Or check specific service
systemctl status some-service.service
# Look for: memory.high events, OOM kills, CPU throttling
```

### Alert on Quota Breach

```ini
# /etc/systemd/system/quota-monitor.service
[Unit]
Description=Monitor cgroup quota breaches

[Service]
Type=simple
ExecStart=/usr/local/bin/quota-alert.sh
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
#!/bin/bash
# /usr/local/bin/quota-alert.sh
# Monitor for cgroup events indicating quota pressure

while true; do
    # Check memory.events for all slices
    for events in /sys/fs/cgroup/*/memory.events; do
        high=$(grep '^high ' "$events" | awk '{print $2}')
        max=$(grep '^max ' "$events" | awk '{print $2}')
        oom_kill=$(grep '^oom_kill ' "$events" | awk '{print $2}')
        
        if [ "$oom_kill" -gt 0 ] 2>/dev/null; then
            logger -p auth.alert "QUOTA BREACH: OOM kill in $(dirname $events) — count=$oom_kill"
        fi
        if [ "$high" -gt 100 ] 2>/dev/null; then
            logger -p auth.warning "QUOTA PRESSURE: memory.high events in $(dirname $events) — count=$high"
        fi
    done
    
    # Check tmpfs upper layer usage
    used=$(df /run/ram-overlay 2>/dev/null | tail -1 | awk '{print $5}' | tr -d '%')
    if [ "$used" -gt 80 ] 2>/dev/null; then
        logger -p auth.alert "OVERLAY FULL: tmpfs upper layer at ${used}% — possible rootkit activity"
    fi
    
    sleep 5
done
```

---

## 11. AUDIT RULES FOR OVERLAY DETECTION

Building on Report 29's audit framework, here are rules specifically for monitoring the RAM overlay environment.

### Watch the Upper Layer Directly

```bash
# /etc/audit/rules.d/50-overlay-trap.rules

## === OVERLAY UPPER LAYER MONITORING ===
## Watch the actual upper layer directory where ALL modifications land

# casper live boot upper layer
-w /cow -p wa -k overlay_write
-w /cow -p a -k overlay_attr

# overlayroot upper layer
-w /media/root-rw/overlay -p wa -k overlay_write

# Custom initramfs overlay upper
-w /run/ram-overlay/upper -p wa -k overlay_write

## === CRITICAL FILE MODIFICATIONS (IN OVERLAY) ===
## These fire when ANYTHING modifies these paths — the modification
## actually lands in the upper layer but auditd sees the merged path

# Binary modifications
-w /usr/bin -p wa -k bin_tamper
-w /usr/sbin -p wa -k sbin_tamper
-w /usr/lib -p wa -k lib_tamper

# Library replacement (from Report 25 — deleted libraries attack)
-w /usr/lib/x86_64-linux-gnu/libc.so.6 -p wa -k libc_tamper
-w /usr/lib/x86_64-linux-gnu/libstdc++.so.6 -p wa -k libstdcpp_tamper
-w /usr/lib/x86_64-linux-gnu/libgcc_s.so.1 -p wa -k libgcc_tamper

# Shared library cache
-w /etc/ld.so.conf -p wa -k ldconfig_tamper
-w /etc/ld.so.conf.d -p wa -k ldconfig_tamper
-w /etc/ld.so.cache -p wa -k ldcache_tamper

## === PROCESS AND MODULE EVENTS ===
# New process execution
-a always,exit -F arch=b64 -S execve -k exec_log

# Kernel module operations
-a always,exit -F arch=b64 -S init_module,finit_module -k module_load
-a always,exit -F arch=b64 -S delete_module -k module_unload

# Mount operations (overlay manipulation)
-a always,exit -F arch=b64 -S mount,umount2 -k mount_op

# Device mapper (rootkit uses DM for NVMe mapping)
-w /dev/mapper -p rwxa -k device_mapper
-a always,exit -F arch=b64 -S ioctl -F a1=0xfd00 -k dm_ioctl

## === BOOT CHAIN PROTECTION ===
-w /boot -p wa -k boot_tamper
-w /boot/efi -p wa -k efi_tamper
-w /etc/grub.d -p wa -k grub_tamper

## === NETWORK (EXFILTRATION DETECTION) ===
-a always,exit -F arch=b64 -S connect -F a0=2 -k net_connect_ipv4
-a always,exit -F arch=b64 -S connect -F a0=10 -k net_connect_ipv6
```

### Search for Overlay Modifications

```bash
# See everything written to the overlay
ausearch -k overlay_write -i

# See binary tampering attempts
ausearch -k bin_tamper -i --start today

# See library replacement (the Report 25 attack vector)
ausearch -k libc_tamper -i

# See all new processes
ausearch -k exec_log --start recent

# Real-time monitoring
aureport --summary
aureport -f --summary  # file access summary
```

### Direct Upper Layer Inspection

Regardless of auditd, you can always **directly inspect** the overlay upper layer to see what changed:

```bash
# For casper live boot
find /cow -type f -newer /cow -ls 2>/dev/null

# For overlayroot
find /media/root-rw/overlay -type f -ls 2>/dev/null

# For custom initramfs overlay
find /run/ram-overlay/upper -type f -ls 2>/dev/null

# Compare against known-good:
# Any file in the upper layer is a MODIFICATION of the base system
diff -rq /media/root-ro/usr/bin /usr/bin 2>/dev/null | head -50
```

### Whiteouts (Deleted Files in Overlay)

When a file is "deleted" in overlayfs, it creates a **whiteout** — a special character device in the upper layer:

```bash
# Find all whiteouts (deleted files) in the overlay
find /cow -type c -ls 2>/dev/null
find /run/ram-overlay/upper -type c -ls 2>/dev/null

# Each whiteout represents a file that existed in the lower layer
# but was "deleted" in the overlay. The rootkit might delete
# security tools this way.
```

---

## 12. DM-VERITY — TAMPER-PROOF BASE LAYER

dm-verity provides cryptographic integrity verification of the read-only base layer. If anything — rootkit, bit-flip, hardware error — modifies the base image, dm-verity detects it.

### What dm-verity Does

```
Hash tree computed at build time → stored separately
Every read from device → hash verified against tree
Mismatch → I/O error (or configured response)
```

### Creating a dm-verity Protected squashfs

```bash
# 1. Create your clean squashfs base image
sudo mksquashfs /path/to/clean-root filesystem.squashfs \
    -comp zstd -Xcompression-level 19 \
    -e /tmp /var/log /var/cache

# 2. Create dm-verity hash tree
veritysetup format filesystem.squashfs filesystem.verity
# Output: Root hash: <SHA256 hash>
# SAVE THIS HASH — it goes in your boot config

# 3. Open with dm-verity verification
veritysetup open filesystem.squashfs verified-root filesystem.verity \
    <root-hash-from-step-2>

# 4. Mount the verified device
mount /dev/mapper/verified-root /mnt/verified -o ro
```

### Boot Integration

The root hash goes into your GRUB config or kernel command line:

```bash
linux /vmlinuz root=/dev/dm-0 \
    dm-mod.create="verified-root,,,ro,0 SECTORS verity 1 ROOT_DEV HASH_DEV 4096 4096 BLOCKS HASH_OFFSET sha256 ROOT_HASH SALT" \
    ...
```

### Why This Matters

The rootkit documented in Report 24 uses **stock Ventoy and stock casper** — it doesn't modify those components. But it could. With dm-verity on your base image:

- Any modification to the squashfs base → **detected and blocked**
- Rootkit can't silently replace system binaries in the base layer
- Combined with overlay monitoring: rootkit can only write to the upper layer, which you're watching

---

## 13. COMPLETE DEFENSIVE CONFIGURATION

Here's the full setup, combining everything from this report and Reports 25-29.

### Architecture

```
EFI Secure Boot (your keys)
  → YOUR signed GRUB (not CN=grub rootkit)
    → Kernel with hardened cmdline (Report 28)
      → initramfs with RAM overlay hook
        → dm-verity verified squashfs (read-only base)
          → overlayfs with capped tmpfs upper (monitored)
            → systemd with cgroup quotas (Report 27)
              → services sandboxed (Report 26)
                → auditd watching everything (Report 29 + this report)
                  → Remote syslog (evidence preservation)
```

### Step-by-Step Setup (overlayroot Method for Installed Mint)

```bash
# 1. Install overlayroot
sudo apt install overlayroot

# 2. Configure RAM overlay
echo 'overlayroot="tmpfs"' | sudo tee /etc/overlayroot.conf

# 3. Disable disk swap, enable zram
sudo swapoff -a
sudo sed -i 's/^.*swap/#&/' /etc/fstab
sudo apt install zram-config

# 4. Install audit rules (from this report + Report 29)
sudo cp /path/to/50-overlay-trap.rules /etc/audit/rules.d/
sudo systemctl restart auditd

# 5. Apply kernel hardening (Report 28)
# Edit /etc/default/grub:
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash \
    init_on_alloc=1 init_on_free=1 \
    slab_nomerge lockdown=confidentiality \
    module.sig_enforce=1 vsyscall=none \
    apparmor=1 security=apparmor \
    mitigations=auto,nosmt"
sudo update-grub

# 6. Apply systemd system-wide hardening (Report 25)
# Edit /etc/systemd/system.conf per Report 25

# 7. Apply per-service sandboxing (Report 26)
# Create drop-in files per Report 26

# 8. Apply cgroup quotas (Report 27)
# Create slice files per Report 27

# 9. Enable remote syslog (preserve evidence off-machine)
# /etc/rsyslog.d/90-remote.conf:
# *.* @your-log-server:514

# 10. Reboot into RAM-overlay mode
sudo reboot
```

### Step-by-Step Setup (toram Method for Live Boot)

```bash
# 1. Create hardened live USB with Mint ISO

# 2. Boot with modified GRUB entry:
linux /casper/vmlinuz boot=casper toram nopersistent \
    quiet splash \
    init_on_alloc=1 init_on_free=1 \
    slab_nomerge lockdown=confidentiality \
    module.sig_enforce=1 vsyscall=none \
    apparmor=1 security=apparmor

# 3. Once booted, deploy audit rules:
sudo cp /path/to/50-overlay-trap.rules /etc/audit/rules.d/
sudo augenrules --load

# 4. Deploy cgroup quotas:
# Copy slice/service files from Report 27

# 5. Start monitoring:
sudo systemd-cgtop &
sudo tail -f /var/log/audit/audit.log &

# 6. Inspect overlay upper layer periodically:
watch -n 10 'find /cow -type f -newer /cow 2>/dev/null | wc -l'
```

---

## 14. CROSS-REFERENCE TO ROOTKIT ATTACK CHAIN

Mapping the rootkit's documented techniques (Report 24) against this report's defenses:

| Rootkit Technique | Report 24 Section | Defense (This Report) |
|-------------------|-------------------|-----------------------|
| Casper live boot from NVMe | §15.18 | YOUR casper toram from YOUR media |
| overlayfs for writable root | §15.18 | YOUR overlay with capped tmpfs + audit |
| squashfs base image | §15.14-15 | dm-verity on YOUR squashfs |
| Ventoy boot framework | §15.14 | Eliminated — you control GRUB directly |
| MOK cert for GRUB signing | §15.19 | Secure Boot with YOUR keys only |
| DM mapping for NVMe access | §15.18 | DevicePolicy=strict blocks DM access per-service |
| Library deletion (Report 25) | §4-5 | Read-only base prevents deletion; audit catches attempts |
| Binary replacement | Implicit | Upper layer monitoring catches all replacements |

### The Fundamental Shift

The rootkit's architecture (casper + overlay + squashfs) is **good architecture**. The problem isn't the technique — it's who controls it. This report takes the same architecture and puts it under YOUR control:

- **Same overlay stack** → but YOU set the tmpfs limits and monitor the upper layer
- **Same squashfs base** → but YOUR image, dm-verity verified
- **Same boot chain** → but YOUR GRUB, YOUR keys, YOUR kernel cmdline
- **Same RAM-based operation** → but with YOUR audit hooks, YOUR cgroup quotas, YOUR remote logging

---

## 15. QUICK REFERENCE CARD

### Boot Parameters

```bash
# Live boot (toram)
boot=casper toram nopersistent

# Installed system (systemd volatile)
systemd.volatile=overlay

# Custom initramfs
ram-overlay
```

### Key Files

| File | Purpose |
|------|---------|
| `/etc/overlayroot.conf` | overlayroot configuration |
| `/etc/default/grub` | Kernel cmdline parameters |
| `/etc/audit/rules.d/50-overlay-trap.rules` | Overlay monitoring audit rules |
| `/etc/systemd/system/system-hardened.slice` | Resource quota slice |
| `/etc/initramfs-tools/scripts/init-bottom/ram-overlay` | Custom overlay hook |

### Inspection Commands

```bash
# What changed in the overlay?
find /cow -type f -ls                              # casper
find /media/root-rw/overlay -type f -ls            # overlayroot
find /run/ram-overlay/upper -type f -ls            # custom

# What was deleted (whiteouts)?
find /cow -type c -ls                              # casper
find /run/ram-overlay/upper -type c -ls            # custom

# Overlay tmpfs usage
df -h /cow                                         # casper
df -h /media/root-rw                               # overlayroot
df -h /run/ram-overlay                             # custom

# Audit log queries
ausearch -k overlay_write -i                       # overlay writes
ausearch -k bin_tamper -i --start today            # binary mods
ausearch -k libc_tamper -i                         # library replacement
aureport -f --summary                              # file access summary

# Resource quota monitoring
systemd-cgtop --recursive                          # live cgroup view
systemctl status system-hardened.slice             # slice status
journalctl -u some.service | grep -i oom           # OOM events
```

### Memory Quick Math

```
16GB RAM total
 - 300MB kernel/initramfs
 - 2.5GB squashfs (toram only)
 - 2.0GB tmpfs upper (capped)
 - 4.0GB zram compressed swap
 = 7.2GB free for applications (toram)
 = 9.7GB free for applications (overlayroot, no squashfs in RAM)
```

---

*This report continues the hardening series (Reports 25-29) and directly addresses the defensive use of RAM-based system operation. The rootkit uses casper+overlay because it's effective architecture. This report takes that same architecture and turns it into a monitored cage. Combined with the resource quotas from Report 27 and the audit framework from Report 29, every action the rootkit takes is either resource-limited, logged, or both.*
