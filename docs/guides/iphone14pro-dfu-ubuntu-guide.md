# iPhone 14 Pro — DFU Restore Guide on Ubuntu (USB-A to Lightning)

**Target device:** iPhone 14 Pro  
**Target firmware:** iOS 26.3.1  
**Host OS:** Ubuntu (22.04 LTS or later recommended)  
**Cable:** USB-A to Lightning  
**Date written:** 2026-03-05

---

## Table of Contents

1. [Background — What is DFU mode?](#1-background--what-is-dfu-mode)
2. [Why DFU keeps disconnecting — root causes](#2-why-dfu-keeps-disconnecting--root-causes)
3. [Prerequisites and software installation](#3-prerequisites-and-software-installation)
4. [Cable and port preparation](#4-cable-and-port-preparation)
5. [Fix USB power management and udev rules](#5-fix-usb-power-management-and-udev-rules)
6. [Entering DFU mode on iPhone 14 Pro — exact sequence](#6-entering-dfu-mode-on-iphone-14-pro--exact-sequence)
7. [Verifying DFU mode from Ubuntu](#7-verifying-dfu-mode-from-ubuntu)
8. [Downloading iOS 26.3.1 IPSW](#8-downloading-ios-2631-ipsw)
9. [Restoring via idevicerestore](#9-restoring-via-idevicerestore)
10. [Troubleshooting disconnection errors](#10-troubleshooting-disconnection-errors)
11. [Quick reference command sheet](#11-quick-reference-command-sheet)

---

## 1. Background — What is DFU mode?

**DFU (Device Firmware Update)** is the lowest-level restore mode on an iPhone. Unlike Recovery Mode, DFU bypasses the iBoot bootloader entirely and communicates directly with the Secure Enclave. This means:

- The screen stays **completely black** (no Apple logo, no USB icon).
- The device is identified by the host as an Apple Mobile Device in DFU mode.
- It is the correct mode for a full firmware restore when normal recovery fails.

DFU is the right choice when:
- The device is stuck in a boot loop.
- Recovery Mode restores fail or abort mid-way.
- You need to install a specific firmware version (downgrade/upgrade).

---

## 2. Why DFU keeps disconnecting — root causes

Disconnection during DFU is one of the most common problems on Linux. There are several causes:

| Cause | Symptoms |
|---|---|
| USB autosuspend (kernel power management) | Device drops after 2–5 seconds; `dmesg` shows `usb X-X: USB disconnect` |
| Missing or wrong udev rules | `idevicerestore` cannot claim the device; "no device found" immediately after DFU entry |
| Low-quality or charging-only USB-A cable | DFU entered but immediately exits; cable lacks data lines |
| USB 3.x controller compatibility | Intermittent drops; try a USB 2.0 port instead |
| `usbmuxd` not running or wrong version | `idevicepair` fails; `idevicerestore` stalls at "waiting for device" |
| SELinux / AppArmor blocking USB access | Permission denied in logs even as root |

---

## 3. Prerequisites and software installation

### 3.1 Update your system

```bash
sudo apt update && sudo apt upgrade -y
```

### 3.2 Install required packages

```bash
sudo apt install -y \
    libimobiledevice-utils \
    usbmuxd \
    ifuse \
    irecovery \
    libusb-1.0-0-dev \
    libssl-dev \
    build-essential \
    git \
    curl \
    usbutils
```

> **Note on `idevicerestore`:** The version in the Ubuntu apt repositories may be outdated. Build from source to ensure iOS 26 support:

```bash
# Install build dependencies
sudo apt install -y autoconf automake libtool pkg-config \
    libplist-dev libimobiledevice-dev libcurl4-openssl-dev \
    libzip-dev libzlib-dev zlib1g-dev

# Clone and build
git clone https://github.com/libimobiledevice/idevicerestore.git
cd idevicerestore
./autogen.sh
make
sudo make install
sudo ldconfig
```

### 3.3 Verify installed versions

```bash
ideviceinfo --version
usbmuxd --version
idevicerestore --version
irecovery --version
```

---

## 4. Cable and port preparation

### 4.1 Confirm your cable carries data

USB-A to Lightning cables fall into two categories:
- **Charge-only cables** — contain only VBUS and GND wires; **will not work for DFU**.
- **Data cables** — contain all four USB wires (VBUS, D-, D+, GND).

**Test your cable:**
```bash
# Plug the iPhone in normally (not in DFU), then run:
lsusb | grep Apple
```
If you see an Apple entry (e.g., `Bus 001 Device 005: ID 05ac:12a8 Apple, Inc. iPhone5/5C/5S/6/SE`), the cable carries data. If nothing appears, the cable is charge-only — **replace it**.

### 4.2 Use a USB 2.0 port

On many Linux systems, USB 3.x controllers introduce timing issues during DFU. Prefer a USB 2.0 port (often the black-coloured ports on desktops, or the ports directly on the motherboard rather than a hub).

If your machine only has USB 3.x, force 2.0 speeds:
```bash
# Find the USB controller PCI address
lspci | grep -i usb

# Check /sys for the xhci controller and disable USB3
# (only do this temporarily for the restore session)
echo 0 | sudo tee /sys/bus/usb/devices/usbX/bDeviceProtocol
```
Alternatively, use a **USB 2.0 hub** as an intermediary — this is the simplest fix.

### 4.3 Plug directly into the computer

Do not use USB hubs (powered or unpowered) during DFU if possible. Plug the Lightning end directly into the computer's port. Hubs introduce timing delays that can cause premature disconnection.

---

## 5. Fix USB power management and udev rules

This is the **most important step** on Ubuntu. Without it, the kernel will suspend the USB device within a few seconds of DFU entry.

### 5.1 Disable USB autosuspend globally (temporary — for this session)

```bash
sudo -i
for f in /sys/bus/usb/devices/*/power/autosuspend_delay_ms; do echo -1 > "$f"; done
for f in /sys/bus/usb/devices/*/power/control; do echo on > "$f"; done
exit
```

### 5.2 Disable USB autosuspend permanently (recommended)

Create or edit `/etc/udev/rules.d/99-usb-autosuspend.rules`:

```bash
sudo tee /etc/udev/rules.d/99-usb-autosuspend.rules > /dev/null << 'EOF'
# Disable autosuspend for all USB devices
ACTION=="add", SUBSYSTEM=="usb", TEST=="power/autosuspend", ATTR{power/autosuspend}="-1"
ACTION=="add", SUBSYSTEM=="usb", TEST=="power/control", ATTR{power/control}="on"
EOF
```

### 5.3 Add Apple DFU udev rules

These rules give your user account (and the `usbmuxd` service) permission to access the Apple DFU device:

```bash
sudo tee /etc/udev/rules.d/39-usbmuxd.rules > /dev/null << 'EOF'
# Apple Mobile Device — Normal mode
SUBSYSTEM=="usb", ENV{DEVTYPE}=="usb_device", ATTR{idVendor}=="05ac", ATTR{idProduct}=="12a8", MODE="0666", GROUP="plugdev"

# Apple Mobile Device — Recovery mode
SUBSYSTEM=="usb", ENV{DEVTYPE}=="usb_device", ATTR{idVendor}=="05ac", ATTR{idProduct}=="1281", MODE="0666", GROUP="plugdev"

# Apple Mobile Device — DFU mode (iPhone 14 Pro and similar)
SUBSYSTEM=="usb", ENV{DEVTYPE}=="usb_device", ATTR{idVendor}=="05ac", ATTR{idProduct}=="1227", MODE="0666", GROUP="plugdev"
SUBSYSTEM=="usb", ENV{DEVTYPE}=="usb_device", ATTR{idVendor}=="05ac", ATTR{idProduct}=="1338", MODE="0666", GROUP="plugdev"

# Catch-all for any Apple USB device
SUBSYSTEM=="usb", ATTR{idVendor}=="05ac", MODE="0660", GROUP="plugdev"
EOF
```

Reload udev rules and add yourself to the `plugdev` group:

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
sudo usermod -aG plugdev "$USER"
# Log out and back in, OR run:
newgrp plugdev
```

### 5.4 Disable kernel USB autosuspend via boot parameter (most robust fix)

Edit `/etc/default/grub`:

```bash
sudo nano /etc/default/grub
```

Find the line starting with `GRUB_CMDLINE_LINUX_DEFAULT` and add `usbcore.autosuspend=-1`:

```
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash usbcore.autosuspend=-1"
```

Save and update GRUB:

```bash
sudo update-grub
# Reboot to apply
sudo reboot
```

After rebooting, verify:
```bash
cat /sys/module/usbcore/parameters/autosuspend
# Should output: -1
```

---

## 6. Entering DFU mode on iPhone 14 Pro — exact sequence

> **Important:** The iPhone 14 Pro uses a **physical Side button** and **Volume buttons**. There is no Home button. The DFU sequence is different from older iPhones.

### Pre-conditions

- The iPhone screen should be **on** (or simply plugged in and powered).
- USB cable is plugged into the computer before you begin.
- `usbmuxd` is running: `sudo systemctl start usbmuxd`

### Step-by-step DFU entry

**Step 1 — Quick press Volume Up**  
Press and immediately release the **Volume Up** button (top-left side of the phone). This is a quick press, not a hold.

**Step 2 — Quick press Volume Down**  
Press and immediately release the **Volume Down** button (below Volume Up). Again, quick press only.

**Step 3 — Hold Side button for exactly 10 seconds**  
Press and hold the **Side button** (right side of the phone) for exactly **10 seconds**. The screen will turn off after about 3 seconds — keep holding.

**Step 4 — After 10 seconds: hold Side button AND Volume Down simultaneously for 5 seconds**  
While still holding the Side button from Step 3, also press and hold the **Volume Down** button. Hold both for **5 seconds**.

**Step 5 — Release Side button only (keep Volume Down held for 5 more seconds)**  
At exactly the 5-second mark of holding both buttons, release the **Side button** only. Continue holding the **Volume Down** button for another **5 seconds**.

**Step 6 — Release Volume Down**  
Release the Volume Down button. The phone screen should remain **completely black**.

### Success indicators

- The iPhone screen is **completely black** (no Apple logo).
- On the Ubuntu terminal, running `lsusb` shows:
  ```
  Bus 001 Device 006: ID 05ac:1227 Apple, Inc. Mobile Device (DFU Mode)
  ```
- Running `irecovery -q` shows `MODE: DFU`.

### If you see the Apple logo

If the Apple logo appears, you entered **Recovery Mode**, not DFU mode. This happens if you held the buttons too long in Step 5. Unplug the cable, wait 10 seconds, and try again from Step 1.

### Visual summary

```
|--- 10 sec ---|--- 5 sec ---|--- 5 sec ---|
  Side btn held  Side+VolDn   VolDn only
                              (Side released)
                                            ^ Release VolDn → DFU
```

---

## 7. Verifying DFU mode from Ubuntu

Run these commands after the device enters DFU:

```bash
# Confirm USB device is visible
lsusb | grep -i apple

# Check irecovery
irecovery -q
# Expected output:
# CONNECTED: DFU Mode
# MODE: DFU

# List with idevicerestore
idevicerestore -l
# Should list your device UDID in DFU mode

# Check kernel log for the connection event
dmesg | tail -20
# Look for: usb X-X: new full-speed USB device number X using xhci_hcd
#           usb X-X: New USB device found, idVendor=05ac, idProduct=1227
```

If `irecovery -q` shows `MODE: Recovery` rather than `MODE: DFU`, the sequence was not quite right — unplug, reboot the phone (hold Side + Volume Down until Apple logo, then release), and retry.

---

## 8. Downloading iOS 26.3.1 IPSW

### Option A — Download from IPSW.me (recommended)

```bash
# Install curl if not already present
sudo apt install -y curl

# Download the iPhone 14 Pro IPSW for iOS 26.3.1
# Replace the URL below with the exact URL from https://ipsw.me/product/iPhone15,2
curl -L -o ~/iOS-26.3.1-iPhone14Pro.ipsw \
  "https://updates.cdn-apple.com/REPLACE_WITH_ACTUAL_URL/iPhone15,2_26.3.1_XXXXX_Restore.ipsw"
```

> **To find the exact URL:** Visit [https://ipsw.me](https://ipsw.me), select **iPhone 14 Pro** (model identifier `iPhone15,2`), then select iOS **26.3.1**. Right-click the download link and copy the direct URL.

### Option B — Use `idevicerestore` auto-download

`idevicerestore` can download the correct IPSW automatically if you omit the `-i` flag (or use `-d` for the latest available):

```bash
# idevicerestore will download the correct IPSW automatically
sudo idevicerestore -d
```

However, specifying the IPSW manually (Option A) gives you more control and lets you verify the file before use.

### Verify the IPSW integrity

```bash
# Check the file is not truncated
ls -lh ~/iOS-26.3.1-iPhone14Pro.ipsw

# Verify it's a valid ZIP (IPSW files are ZIP archives)
unzip -t ~/iOS-26.3.1-iPhone14Pro.ipsw | tail -5
```

---

## 9. Restoring via idevicerestore

### 9.1 Ensure usbmuxd is running

```bash
sudo systemctl enable usbmuxd
sudo systemctl start usbmuxd
systemctl status usbmuxd
```

### 9.2 Run the restore

With the device in DFU mode and the IPSW downloaded:

```bash
sudo idevicerestore -d ~/iOS-26.3.1-iPhone14Pro.ipsw
```

**Flags explained:**

| Flag | Meaning |
|---|---|
| `-d` | Debug output (verbose) — essential for diagnosing disconnections |
| `-e` | Erase device (factory restore, recommended for clean install) |
| `-w` | Wait for device (use if device is not yet in DFU when you run the command) |

Full recommended command:

```bash
sudo idevicerestore -d -e ~/iOS-26.3.1-iPhone14Pro.ipsw
```

### 9.3 What to expect during restore

The restore process has several phases — each phase changes the USB product ID. This is normal:

1. **DFU mode detected** (`05ac:1227`) → idevicerestore uploads iBSS
2. **Recovery mode** (`05ac:1281`) → idevicerestore uploads iBEC, then ramdisk
3. **Restore mode** → kernel extensions and filesystem are written
4. **Reboot** → device restores, Apple logo with progress bar appears
5. **Completion** → device reboots into iOS Setup Assistant

Total time: approximately **10–25 minutes** depending on connection speed (IPSW download) and USB speed.

---

## 10. Troubleshooting disconnection errors

### Error: `ERROR: Unable to find device in DFU mode after X seconds`

**Cause:** Device exited DFU before idevicerestore could connect.  
**Fix:**
1. Apply the USB autosuspend fix from Section 5.
2. Re-enter DFU immediately before running `idevicerestore`.
3. Use `idevicerestore -w` to make it wait: `sudo idevicerestore -d -w ~/iOS-26.3.1-iPhone14Pro.ipsw`

---

### Error: `ERROR: Unable to send iBSS to device` or device disconnects mid-flash

**Cause:** USB instability during file transfer.  
**Fix sequence:**
1. Try a different physical USB port (preferably USB 2.0).
2. Use a powered USB 2.0 hub as an intermediary.
3. Confirm USB autosuspend is fully disabled (Section 5.4).
4. Run with `sudo` to ensure device access permissions.

---

### Error: `[ERROR] Unable to connect to device in DFU mode`

**Cause:** Missing udev rules or `usbmuxd` not running.  
**Fix:**
```bash
sudo systemctl restart usbmuxd
sudo udevadm control --reload-rules && sudo udevadm trigger
# Re-enter DFU mode and retry
```

---

### Error: Device shows in `lsusb` but `irecovery -q` says "no device found"

**Cause:** Another process (e.g., `gvfs-afc-volume-monitor`, Nautilus) has claimed the USB device.  
**Fix:**
```bash
# Kill competing processes
sudo killall usbmuxd 2>/dev/null || true
sudo killall gvfs-afc-volume-monitor 2>/dev/null || true
sudo systemctl restart usbmuxd
```

---

### DFU sequence timing issues (most common disconnection cause)

If you are finding the button sequence difficult to time precisely, here is a physical technique:

1. Use a timer app on another device (phone/tablet) set for **10 seconds** and **5 seconds**.
2. Practice the button sequence without the cable plugged in first.
3. The exact timing that works for most people on iPhone 14 Pro:
   - Steps 1 and 2 (Volume Up, Volume Down): press and release in under 0.5 seconds each.
   - Step 3 (Side button hold): exactly 10 seconds — count to yourself: "one-one-thousand, two-one-thousand..."
   - Step 4 (add Volume Down): hold both for 5 seconds.
   - Step 5 (release Side, keep Volume Down): 5 more seconds.

---

### Check dmesg for real-time USB events

In a second terminal, monitor USB events during DFU entry:

```bash
sudo dmesg -w | grep -E "usb|Apple|05ac"
```

This lets you see exactly when the device connects/disconnects and what error code the kernel reports.

---

### USB-A to Lightning specific: cable current draw

Some USB-A ports on laptops will cut power to a USB device if it draws unexpected current in DFU mode. If your cable supports it, try:

```bash
# Check if USB port is in a low-power state
cat /sys/bus/usb/devices/*/power/runtime_status | grep -v "unsupported"
```

If you see `suspended`, the autosuspend fix in Section 5 was not fully applied. Reboot after making the changes.

---

## 11. Quick reference command sheet

```bash
# --- SETUP ---
sudo systemctl start usbmuxd
sudo udevadm control --reload-rules && sudo udevadm trigger

# --- VERIFY DFU ---
lsusb | grep -i apple
irecovery -q
dmesg | tail -20

# --- DISABLE USB AUTOSUSPEND (session-only) ---
sudo sh -c 'for f in /sys/bus/usb/devices/*/power/control; do echo on > "$f"; done'
sudo sh -c 'for f in /sys/bus/usb/devices/*/power/autosuspend_delay_ms; do echo -1 > "$f"; done'

# --- KILL COMPETING PROCESSES ---
sudo killall gvfs-afc-volume-monitor 2>/dev/null || true
sudo systemctl restart usbmuxd

# --- RESTORE ---
sudo idevicerestore -d -e ~/iOS-26.3.1-iPhone14Pro.ipsw

# --- MONITOR USB EVENTS (separate terminal) ---
sudo dmesg -w | grep -E "usb|Apple|05ac"
```

---

## Summary

The most common reason DFU disconnects on Ubuntu with a USB-A to Lightning cable is **Linux USB autosuspend**. The kernel suspends idle USB devices after 2 seconds by default, which is shorter than the time `idevicerestore` needs to upload the initial bootloader (iBSS). The fix is to add `usbcore.autosuspend=-1` to the kernel boot parameters (Section 5.4) and add correct udev rules (Section 5.3). After those changes, the DFU restore process is reliable.

If disconnections continue after applying all fixes, the most effective hardware workaround is to use a **USB 2.0 hub** between the computer and the iPhone — this isolates the device from the host controller's power management.
