# Report 28 — Kernel Command-Line & sysctl Security Hardening

**Classification:** SYSTEM HARDENING — FULL REFERENCE GUIDE  
**Prepared by:** ClaudeMKII (MK2PK)  
**Report Date:** 2026-04-18  
**Sources:** kernel-command-line(7), kernel-parameters.html, KSPP recommended settings, sysctl(8), proc(5)  
**System:** ASUS PRIME B460M-A, Intel i7-10700 (8C/16T, 2.9GHz base / 4.8GHz boost), 16GB RAM  
**OS:** Linux Mint 22.3 Zena (Ubuntu 24.04 base)  
**Kernels:** 6.14.0-37-generic, 6.17.0-20-generic  
**Builds on:** Reports 24 (rootkit boot chain), 25-27 (systemd hardening series)  
**Identifier:** ClaudeMKII-Seed-20260317

---

## TABLE OF CONTENTS

1. [Scope and Context](#1-scope-and-context)
2. [Boot Parameters — Memory Protection](#2-boot-parameters--memory-protection)
3. [Boot Parameters — Kernel Lockdown](#3-boot-parameters--kernel-lockdown)
4. [Boot Parameters — CPU Mitigations](#4-boot-parameters--cpu-mitigations)
5. [Boot Parameters — KASLR and Randomisation](#5-boot-parameters--kaslr-and-randomisation)
6. [Boot Parameters — Module and Debug Controls](#6-boot-parameters--module-and-debug-controls)
7. [Boot Parameters — vsyscall and Legacy Interfaces](#7-boot-parameters--vsyscall-and-legacy-interfaces)
8. [Boot Parameters — LSM and Audit](#8-boot-parameters--lsm-and-audit)
9. [Boot Parameters — systemd-Specific](#9-boot-parameters--systemd-specific)
10. [Boot Parameters — dm-verity and Integrity](#10-boot-parameters--dm-verity-and-integrity)
11. [sysctl — Kernel Information Restriction](#11-sysctl--kernel-information-restriction)
12. [sysctl — Memory Protection](#12-sysctl--memory-protection)
13. [sysctl — Filesystem Protection](#13-sysctl--filesystem-protection)
14. [sysctl — Network Hardening (IPv4)](#14-sysctl--network-hardening-ipv4)
15. [sysctl — Network Hardening (IPv6)](#15-sysctl--network-hardening-ipv6)
16. [sysctl — Miscellaneous Security](#16-sysctl--miscellaneous-security)
17. [Complete Hardened GRUB Line for ASUS B460M-A](#17-complete-hardened-grub-line-for-asus-b460m-a)
18. [Complete sysctl Hardening File](#18-complete-sysctl-hardening-file)
19. [Appendix: i7-10700 CPU Vulnerability Status](#appendix-i7-10700-cpu-vulnerability-status)

---

## 1. Scope and Context

This report covers two layers of kernel hardening:

1. **Boot-time parameters** — set in GRUB config (`/etc/default/grub` → `GRUB_CMDLINE_LINUX`) or directly on the kernel command line. These cannot be changed at runtime.
2. **Runtime parameters** — set via `sysctl` in `/etc/sysctl.d/*.conf` or `/etc/sysctl.conf`. These CAN be changed at runtime but should be set at boot.

### Investigation Context

Report 24 documented a rootkit that:
- Replaced GRUB with a MOK-signed variant that ignored the installed GRUB config
- Booted a Ventoy-based casper live overlay via `rdinit=/vtoy/vtoy`
- Used kernel 7.0.0-10 while the installed kernel was 6.8.0-41

**Kernel command-line parameters would have been bypassed** by this attack because the rootkit's GRUB loaded its own kernel with its own command line. However, hardening the GRUB config:
1. Makes the legitimate boot path secure
2. Provides a baseline to detect deviation (if booted kernel doesn't have expected params → compromised)
3. Can be verified at runtime via `/proc/cmdline`

---

## 2. Boot Parameters — Memory Protection

### 2.1 init_on_alloc=

| Property | Value |
|----------|-------|
| Takes | 0 or 1 |
| Default | 0 (most distros), some set 1 |
| Effect | Zeros all page allocator and slab allocator memory on allocation |
| Performance | ~1% overhead on average |
| Kernel config | `CONFIG_INIT_ON_ALLOC_DEFAULT_ON` |

**Hardening: `init_on_alloc=1`** — Prevents information leaks between processes via recycled memory.

### 2.2 init_on_free=

| Property | Value |
|----------|-------|
| Takes | 0 or 1 |
| Default | 0 |
| Effect | Zeros all page allocator and slab allocator memory on free |
| Performance | ~1-5% overhead (higher than init_on_alloc) |
| Kernel config | `CONFIG_INIT_ON_FREE_DEFAULT_ON` |

**Hardening: `init_on_free=1`** — Prevents use-after-free information leaks. Higher overhead than init_on_alloc but stronger protection.

### 2.3 page_poison=

| Property | Value |
|----------|-------|
| Takes | 0 or 1 |
| Default | 0 |
| Effect | Fills freed pages with poison patterns to detect use-after-free |
| Kernel config | `CONFIG_PAGE_POISONING` |
| Note | Largely superseded by init_on_free on modern kernels |

**Hardening: `page_poison=1`** — Extra safety net, works alongside init_on_free.

### 2.4 slab_nomerge

| Property | Value |
|----------|-------|
| Takes | (flag, no value) |
| Default | Merging enabled |
| Effect | Disables slab cache merging — prevents cross-cache attacks |
| Performance | Slightly more memory usage |
| Kernel config | `CONFIG_SLAB_MERGE_DEFAULT` |

**Hardening: `slab_nomerge`** — Makes heap exploitation significantly harder by preventing objects of different types from sharing slab caches.

### 2.5 slub_debug=

| Property | Value |
|----------|-------|
| Takes | Flags: F (free check), Z (red zoning), P (poisoning), U (tracking), T (tracing) |
| Default | Off |
| Common setting | `slub_debug=FZP` |
| Performance | Significant overhead — debugging only |

**Hardening: `slub_debug=FZ`** for production (basic checks), `slub_debug=FZPU` for investigation/debugging.

### 2.6 pti=

| Property | Value |
|----------|-------|
| Takes | `on`, `off`, `auto` |
| Default | `auto` (enabled on vulnerable CPUs) |
| Effect | Page Table Isolation — separates kernel and user page tables (Meltdown mitigation) |

**Hardening: `pti=on`** — Force-enables even if CPU claims it's not needed.

---

## 3. Boot Parameters — Kernel Lockdown

### 3.1 lockdown=

| Property | Value |
|----------|-------|
| Takes | `none`, `integrity`, `confidentiality` |
| Default | `none` (most distros) or controlled by Secure Boot |
| Kernel config | `CONFIG_SECURITY_LOCKDOWN_LSM` |

| Level | Restrictions |
|-------|-------------|
| `none` | No restrictions |
| `integrity` | Blocks: module parameters modifying hardware, kexec of unsigned images, hibernation, direct PCI BAR access, raw I/O port access, raw MSR access, modification of ACPI tables, direct PCMCIA CIS storage, BPF write to user RAM, userspace writing to hardware |
| `confidentiality` | Above + blocks: `/dev/mem`, `/dev/kmem`, `/dev/port`, `/proc/kcore`, BPF read of kernel RAM, perf_event access |

**Hardening: `lockdown=confidentiality`** — Maximum protection. Blocks ALL direct kernel/hardware memory access.

**Note:** Ubuntu/Mint enable `integrity` automatically when Secure Boot is active.

**Investigation note from Report 24:** The rootkit used a MOK-signed GRUB binary. Lockdown with Secure Boot would have required valid signatures, but the attacker enrolled their own MOK key (`CN=grub`). Lockdown alone is insufficient — MOK key audit is also needed.

---

## 4. Boot Parameters — CPU Mitigations

### 4.1 mitigations=

| Property | Value |
|----------|-------|
| Takes | `off`, `auto`, `auto,nosmt` |
| Default | `auto` |
| Added | Kernel 5.2+ |

| Value | Effect |
|-------|--------|
| `off` | Disables ALL CPU mitigations — **NEVER use in production** |
| `auto` | Enables all mitigations for detected CPU |
| `auto,nosmt` | Above + disables SMT (hyperthreading) for maximum security |

**Hardening: `mitigations=auto`** — Don't disable SMT on i7-10700 unless specifically needed (it halves your effective core count from 16T to 8T).

### 4.2 i7-10700 Specific Mitigations

The i7-10700 (Comet Lake, 10th gen) is affected by:

| Vulnerability | Parameter | Recommended |
|--------------|-----------|-------------|
| Spectre v1 | (kernel patches, no cmdline) | Default |
| Spectre v2 | `spectre_v2=on` | Default auto-enabled |
| Meltdown | `pti=on` | Default auto-enabled |
| MDS | `mds=full` | Default auto-enabled |
| TSX Async Abort | `tsx=off` or `tsx_async_abort=full` | `tsx=off` |
| L1 Terminal Fault | `l1tf=full,force` | Default auto-enabled |
| SRBDS (Special Register Buffer) | `srbds=on` | Default auto-enabled |
| Retbleed | `retbleed=auto` | Default |
| MMIO Stale Data | `mmio_stale_data=full` | Default |

**Kernel 6.17+ (on your ASUS system):** The new "Attack Vector Controls" grouping in 6.17 allows fine-grained control:
- `mitigations=auto,no_user_kernel` — disable user↔kernel mitigations (unsafe)
- `mitigations=auto,no_user_user` — disable user↔user mitigations (unsafe)

**Hardening: `mitigations=auto tsx=off`** — Auto-enables all needed mitigations, explicitly kills TSX.

---

## 5. Boot Parameters — KASLR and Randomisation

### 5.1 KASLR (Kernel Address Space Layout Randomisation)

| Property | Value |
|----------|-------|
| Default | Enabled (since ~kernel 4.12 on x86-64) |
| Disable | `nokaslr` |
| Kernel config | `CONFIG_RANDOMIZE_BASE` |

**Hardening:** Do NOT add `nokaslr`. KASLR is on by default and should stay on.

### 5.2 randomize_kstack_offset=

| Property | Value |
|----------|-------|
| Takes | 0 or 1 |
| Default | Distro-dependent |
| Effect | Randomises kernel stack offset on each syscall |
| Kernel config | `CONFIG_RANDOMIZE_KSTACK_OFFSET_DEFAULT` |

**Hardening: `randomize_kstack_offset=1`**

---

## 6. Boot Parameters — Module and Debug Controls

### 6.1 module.sig_enforce

| Property | Value |
|----------|-------|
| Takes | (flag, no value) |
| Default | Off (unless Secure Boot active) |
| Effect | Only loads kernel modules with valid signatures |
| Kernel config | `CONFIG_MODULE_SIG_FORCE` |

**Hardening: `module.sig_enforce`** — Critical. Prevents loading unsigned kernel modules. The rootkit in Report 24 would need signed modules to persist.

### 6.2 modules_disabled (sysctl)

Not a boot param — see sysctl section 16.

### 6.3 debugfs=

| Property | Value |
|----------|-------|
| Takes | `on`, `off`, `no-mount` |
| Default | `on` |
| Effect | Controls debugfs availability |

**Hardening: `debugfs=off`** — Debugfs exposes sensitive kernel information. Disable in production.

### 6.4 oops=panic

| Property | Value |
|----------|-------|
| Takes | `panic` |
| Default | Continue execution after oops |
| Effect | Kernel panics on oops instead of continuing |

**Hardening: `oops=panic`** — Prevents exploitation of corrupted kernel state after oops.

---

## 7. Boot Parameters — vsyscall and Legacy Interfaces

### 7.1 vsyscall=

| Property | Value |
|----------|-------|
| Takes | `none`, `emulate`, `xonly`, `native` |
| Default | `emulate` on most distros |
| Effect | Controls legacy vsyscall mechanism |

| Value | Security | Compatibility |
|-------|----------|--------------|
| `none` | Best — no vsyscall mapping at all | May break very old binaries |
| `emulate` | Good — emulated (slow), no executable mapping | Safe default |
| `xonly` | Medium — executable but not readable | Some protection |
| `native` | Worst — fixed-address executable mapping → trivial ROP gadget source | Never use |

**Hardening: `vsyscall=none`** — Unless you have very old (pre-glibc 2.14, ~2011) binaries.

---

## 8. Boot Parameters — LSM and Audit

### 8.1 security= / lsm=

| Property | Value |
|----------|-------|
| Takes | LSM name(s) |
| Default | Distro-defined (Ubuntu/Mint: `apparmor`) |
| Examples | `security=apparmor`, `lsm=lockdown,yama,integrity,apparmor` |

### 8.2 apparmor=

| Property | Value |
|----------|-------|
| Takes | 0 or 1 |
| Default | 1 (Ubuntu/Mint) |
| Effect | Enables/disables AppArmor LSM |

**Hardening: Leave enabled.** Ubuntu/Mint ships with AppArmor profiles for many services.

### 8.3 audit=

| Property | Value |
|----------|-------|
| Takes | 0 or 1 |
| Default | 0 on most distros |
| Effect | Enables kernel audit subsystem |

**Hardening: `audit=1`** — Required for auditd, audit rules, and syscall logging.

### 8.4 audit_backlog_limit=

| Property | Value |
|----------|-------|
| Takes | Integer |
| Default | 64 (kernel default, often too low) |
| Effect | Size of boot-time audit message queue |

**Hardening: `audit_backlog_limit=8192`** — Prevents early-boot audit messages from being dropped.

---

## 9. Boot Parameters — systemd-Specific

These are from `kernel-command-line(7)` — the systemd man page covered earlier.

| Parameter | Effect | Hardening |
|-----------|--------|-----------|
| `systemd.confirm_spawn=` | Prompts before spawning processes | Debug only |
| `systemd.volatile=` | Stateless boot (tmpfs root) | Forensics use |
| `systemd.mask=UNIT` | Mask specific units at boot | Block known-bad services |
| `systemd.wants=UNIT` | Start extra units | Add audit/monitoring |
| `systemd.debug_shell` | Emergency debug shell on tty9 | **Disable in production** |
| `systemd.setenv=VAR=val` | Set environment variables | — |
| `systemd.set_credential=` | Pass credentials via cmdline | — |
| `systemd.hostname=` | Override hostname at boot | — |
| `systemd.default_timeout_start_sec=` | Override DefaultTimeoutStartSec | — |
| `systemd.watchdog_sec=` | Override watchdog timeouts | — |
| `systemd.log_level=` | System manager log level | — |
| `systemd.log_target=` | Log target (journal, kmsg, etc.) | — |
| `systemd.service_watchdogs=` | Enable/disable service watchdogs | — |

**Hardening:** Do NOT set `systemd.debug_shell` — it provides root access without authentication on tty9.

---

## 10. Boot Parameters — dm-verity and Integrity

| Parameter | Effect |
|-----------|--------|
| `roothash=HASH` | Root filesystem dm-verity hash |
| `systemd.verity=1` | Enable dm-verity for root |
| `systemd.verity_root_data=` | Path to verity data device |
| `systemd.verity_root_hash=` | Root hash |
| `systemd.verity_root_options=` | dm-verity options |
| `usrhash=HASH` | /usr filesystem dm-verity hash |

**Note:** dm-verity provides read-only integrity verification. It's used by immutable OS designs (ChromeOS, CoreOS). For a standard Mint install, this is not typically used, but could be implemented for `/usr/` integrity.

---

## 11. sysctl — Kernel Information Restriction

### 11.1 kernel.kptr_restrict

| Value | Effect |
|-------|--------|
| 0 | Kernel pointers visible to everyone |
| 1 | Kernel pointers hidden unless `CAP_SYSLOG` |
| 2 | Kernel pointers always hidden (printed as 0) |

**Hardening: `kernel.kptr_restrict = 2`** — Prevents leaking kernel addresses that aid exploitation.

### 11.2 kernel.dmesg_restrict

| Value | Effect |
|-------|--------|
| 0 | Any user can read dmesg |
| 1 | Only root/CAP_SYSLOG can read dmesg |

**Hardening: `kernel.dmesg_restrict = 1`** — Kernel logs contain sensitive information (addresses, driver details).

### 11.3 kernel.perf_event_paranoid

| Value | Effect |
|-------|--------|
| -1 | No restrictions |
| 0 | Allow all users to collect non-kernel data |
| 1 | Only allow kernel data for root |
| 2 | Disallow kernel profiling entirely |
| 3 | Disallow ALL performance monitoring (Debian/Ubuntu extension) |

**Hardening: `kernel.perf_event_paranoid = 3`** — Performance counters can be used for side-channel attacks.

### 11.4 kernel.yama.ptrace_scope

| Value | Effect |
|-------|--------|
| 0 | Any process can ptrace any other (same UID) |
| 1 | Only direct parent can ptrace child |
| 2 | Only root with CAP_SYS_PTRACE can ptrace |
| 3 | No process can ptrace at all |

**Hardening: `kernel.yama.ptrace_scope = 2`** — Use 3 if no debuggers needed. Use 2 if you need gdb as root.

### 11.5 kernel.printk

| Format | `current default minimum boot-time-default` |
|--------|---------------------------------------------|
| Default | `4 4 1 7` |

**Hardening: `kernel.printk = 3 3 3 3`** — Restricts console output to errors and above.

### 11.6 kernel.unprivileged_bpf_disabled

| Value | Effect |
|-------|--------|
| 0 | Unprivileged BPF allowed |
| 1 | Permanently disabled (survives sysctl reset) |
| 2 | Disabled but can be re-enabled |

**Hardening: `kernel.unprivileged_bpf_disabled = 1`** — BPF is a powerful attack primitive.

### 11.7 kernel.kexec_load_disabled

| Value | Effect |
|-------|--------|
| 0 | kexec allowed |
| 1 | kexec permanently disabled (one-way toggle) |

**Hardening: `kernel.kexec_load_disabled = 1`** — Prevents loading a new kernel from userspace.

---

## 12. sysctl — Memory Protection

### 12.1 vm.mmap_min_addr

| Default | Usually 65536 |
|---------|---------------|
| Effect | Minimum virtual address for mmap — prevents NULL pointer dereference exploits |

**Hardening: `vm.mmap_min_addr = 65536`** (or higher).

### 12.2 vm.mmap_rnd_bits / vm.mmap_rnd_compat_bits

| Default | 28 / 8 (x86-64) |
|---------|-----------------|
| Effect | Bits of randomness in mmap addresses |

**Hardening: `vm.mmap_rnd_bits = 32`** and `vm.mmap_rnd_compat_bits = 16`** — Maximise ASLR entropy.

### 12.3 vm.unprivileged_userfaultfd

| Value | Effect |
|-------|--------|
| 0 | Only root can use userfaultfd |
| 1 | Anyone can use userfaultfd |

**Hardening: `vm.unprivileged_userfaultfd = 0`** — userfaultfd is commonly used in exploits.

---

## 13. sysctl — Filesystem Protection

### 13.1 fs.protected_hardlinks / fs.protected_symlinks

| Value | Effect |
|-------|--------|
| 0 | No protection |
| 1 | Prevents hardlink/symlink attacks in world-writable sticky directories |

**Hardening: Both `= 1`** (default on modern kernels).

### 13.2 fs.protected_fifos / fs.protected_regular

| Value | Effect |
|-------|--------|
| 0 | No protection |
| 1 | Prevents O_CREAT on existing FIFOs/regular files in sticky dirs not owned by caller |
| 2 | Same but also applies to group-writable dirs |

**Hardening: Both `= 2`**

### 13.3 fs.suid_dumpable

| Value | Effect |
|-------|--------|
| 0 | No core dumps for SUID processes |
| 1 | Core dumps allowed (insecure) |
| 2 | Core dumps restricted to root-readable pipes (suidsafe) |

**Hardening: `fs.suid_dumpable = 0`** — SUID core dumps can leak privileged memory.

---

## 14. sysctl — Network Hardening (IPv4)

### 14.1 Source Routing and Redirects

```ini
# Disable source routing — prevents routing table manipulation
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.conf.default.accept_source_route = 0

# Disable ICMP redirects — prevents gateway hijacking
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0

# Don't send ICMP redirects — this machine is not a router
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.default.send_redirects = 0

# Disable secure redirects
net.ipv4.conf.all.secure_redirects = 0
net.ipv4.conf.default.secure_redirects = 0
```

### 14.2 Spoofing Protection

```ini
# Reverse path filtering — drop packets with spoofed source addresses
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1
```

### 14.3 ICMP Protection

```ini
# Ignore broadcast pings (smurf attack prevention)
net.ipv4.icmp_echo_ignore_broadcasts = 1

# Ignore bogus ICMP error responses
net.ipv4.icmp_ignore_bogus_error_responses = 1

# Rate limit ICMP messages
net.ipv4.icmp_ratelimit = 100
```

### 14.4 TCP Protection

```ini
# SYN cookies — protect against SYN flood attacks
net.ipv4.tcp_syncookies = 1

# Disable TCP timestamps — prevents uptime fingerprinting
net.ipv4.tcp_timestamps = 0

# Increase SYN backlog
net.ipv4.tcp_max_syn_backlog = 2048

# Reduce SYN-ACK retries
net.ipv4.tcp_synack_retries = 2
net.ipv4.tcp_syn_retries = 5

# Disable TCP SACK (Selective ACKs) — has had CVEs (CVE-2019-11477)
# net.ipv4.tcp_sack = 0  # Only if not needed for WAN performance
```

### 14.5 Martian Logging

```ini
# Log packets with impossible source addresses
net.ipv4.conf.all.log_martians = 1
net.ipv4.conf.default.log_martians = 1
```

### 14.6 IP Forwarding

```ini
# Disable IPv4 forwarding (not a router)
net.ipv4.ip_forward = 0
```

---

## 15. sysctl — Network Hardening (IPv6)

```ini
# If IPv6 is not used, disable it entirely
net.ipv6.conf.all.disable_ipv6 = 1
net.ipv6.conf.default.disable_ipv6 = 1
net.ipv6.conf.lo.disable_ipv6 = 1

# If IPv6 IS used, harden it:
net.ipv6.conf.all.accept_redirects = 0
net.ipv6.conf.default.accept_redirects = 0
net.ipv6.conf.all.accept_source_route = 0
net.ipv6.conf.default.accept_source_route = 0
net.ipv6.conf.all.accept_ra = 0           # Don't accept Router Advertisements
net.ipv6.conf.default.accept_ra = 0
net.ipv6.conf.all.use_tempaddr = 2        # Use privacy extensions
net.ipv6.conf.default.use_tempaddr = 2
```

---

## 16. sysctl — Miscellaneous Security

### 16.1 kernel.modules_disabled

| Value | Effect |
|-------|--------|
| 0 | Module loading allowed |
| 1 | Module loading permanently disabled (one-way toggle) |

**Hardening: `kernel.modules_disabled = 1`** — Set AFTER all needed modules are loaded at boot. This is a one-way switch — once set to 1, cannot be changed back without reboot.

### 16.2 kernel.sysrq

| Value | Effect |
|-------|--------|
| 0 | Disable all SysRq functions |
| 1 | Enable all |
| Bitmask | Fine-grained control |

| Bit | Value | Function |
|-----|-------|----------|
| 0 | 1 | Enable control of SysRq logging level |
| 1 | 2 | Enable control of console logging level |
| 2 | 4 | Enable dumping of registers |
| 3 | 8 | Enable sync |
| 4 | 16 | Enable remount read-only |
| 5 | 32 | Enable signals (SAK, SIGTERM, SIGKILL) |
| 6 | 64 | Allow OOM killer |
| 7 | 128 | Allow restart/kexec |
| 8 | 256 | Allow nice adjustment |

**Hardening: `kernel.sysrq = 176`** (sync + remount read-only + restart = 8+16+128+... better just use `kernel.sysrq = 4` for absolute minimum or `0` to disable entirely).

For most hardened systems: **`kernel.sysrq = 0`** — or `kernel.sysrq = 176` (only sync/remount/restart for emergency recovery).

### 16.3 kernel.core_uses_pid

**Hardening: `kernel.core_uses_pid = 1`** — Append PID to core dump filenames to prevent overwriting.

### 16.4 kernel.randomize_va_space

| Value | Effect |
|-------|--------|
| 0 | No ASLR |
| 1 | Randomise shared libraries, stack, mmap, VDSO |
| 2 | Full randomisation (above + brk/heap) |

**Hardening: `kernel.randomize_va_space = 2`** (should be default, but verify).

### 16.5 net.core.bpf_jit_harden

| Value | Effect |
|-------|--------|
| 0 | No BPF JIT hardening |
| 1 | Harden for unprivileged users |
| 2 | Harden for all users |

**Hardening: `net.core.bpf_jit_harden = 2`** — Prevents BPF JIT spraying attacks.

---

## 17. Complete Hardened GRUB Line for ASUS B460M-A

Edit `/etc/default/grub`:

```bash
GRUB_CMDLINE_LINUX="init_on_alloc=1 init_on_free=1 slab_nomerge page_poison=1 pti=on vsyscall=none lockdown=confidentiality mitigations=auto tsx=off randomize_kstack_offset=1 module.sig_enforce debugfs=off oops=panic audit=1 audit_backlog_limit=8192"
```

Then:
```bash
sudo update-grub
# Or for UEFI systems with grub:
sudo grub-mkconfig -o /boot/grub/grub.cfg
```

### Breakdown

| Parameter | Purpose |
|-----------|---------|
| `init_on_alloc=1` | Zero allocated memory |
| `init_on_free=1` | Zero freed memory |
| `slab_nomerge` | Prevent cross-cache attacks |
| `page_poison=1` | Poison freed pages |
| `pti=on` | Force page table isolation |
| `vsyscall=none` | Remove vsyscall mapping |
| `lockdown=confidentiality` | Maximum kernel lockdown |
| `mitigations=auto` | Enable all CPU mitigations |
| `tsx=off` | Disable TSX (vulnerable on i7-10700) |
| `randomize_kstack_offset=1` | Randomise kernel stack |
| `module.sig_enforce` | Only signed modules |
| `debugfs=off` | Remove debugfs |
| `oops=panic` | Panic on kernel bugs |
| `audit=1` | Enable audit subsystem |
| `audit_backlog_limit=8192` | Large audit buffer |

### Verify After Reboot

```bash
cat /proc/cmdline
# Should contain all the above parameters
```

---

## 18. Complete sysctl Hardening File

Save as `/etc/sysctl.d/99-hardening.conf`:

```ini
# =============================================================
# KERNEL SECURITY HARDENING — ASUS PRIME B460M-A / i7-10700
# /etc/sysctl.d/99-hardening.conf
# Apply: sudo sysctl --system
# =============================================================

# --- Kernel Information Restriction ---
kernel.kptr_restrict = 2
kernel.dmesg_restrict = 1
kernel.perf_event_paranoid = 3
kernel.yama.ptrace_scope = 2
kernel.printk = 3 3 3 3
kernel.unprivileged_bpf_disabled = 1
kernel.kexec_load_disabled = 1

# --- Memory Protection ---
vm.mmap_min_addr = 65536
vm.mmap_rnd_bits = 32
vm.mmap_rnd_compat_bits = 16
vm.unprivileged_userfaultfd = 0

# --- Filesystem Protection ---
fs.protected_hardlinks = 1
fs.protected_symlinks = 1
fs.protected_fifos = 2
fs.protected_regular = 2
fs.suid_dumpable = 0

# --- Process ---
kernel.core_uses_pid = 1
kernel.randomize_va_space = 2
kernel.sysrq = 0

# --- BPF ---
net.core.bpf_jit_harden = 2

# --- IPv4 Hardening ---
net.ipv4.ip_forward = 0
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.conf.default.accept_source_route = 0
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.default.send_redirects = 0
net.ipv4.conf.all.secure_redirects = 0
net.ipv4.conf.default.secure_redirects = 0
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1
net.ipv4.conf.all.log_martians = 1
net.ipv4.conf.default.log_martians = 1
net.ipv4.icmp_echo_ignore_broadcasts = 1
net.ipv4.icmp_ignore_bogus_error_responses = 1
net.ipv4.icmp_ratelimit = 100
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_timestamps = 0
net.ipv4.tcp_max_syn_backlog = 2048
net.ipv4.tcp_synack_retries = 2
net.ipv4.tcp_syn_retries = 5

# --- IPv6 Hardening (disable if not used) ---
# Uncomment if IPv6 is not needed:
# net.ipv6.conf.all.disable_ipv6 = 1
# net.ipv6.conf.default.disable_ipv6 = 1
# net.ipv6.conf.lo.disable_ipv6 = 1

# If IPv6 IS used:
net.ipv6.conf.all.accept_redirects = 0
net.ipv6.conf.default.accept_redirects = 0
net.ipv6.conf.all.accept_source_route = 0
net.ipv6.conf.default.accept_source_route = 0
net.ipv6.conf.all.accept_ra = 0
net.ipv6.conf.default.accept_ra = 0

# --- Module loading (set to 1 AFTER boot, via separate script) ---
# kernel.modules_disabled = 1
# WARNING: One-way toggle. Uncomment only if you're sure all modules are loaded.
```

### Apply

```bash
sudo sysctl --system
# Or:
sudo sysctl -p /etc/sysctl.d/99-hardening.conf

# Verify:
sysctl kernel.kptr_restrict kernel.dmesg_restrict kernel.perf_event_paranoid
```

### Module Lockdown Script

For `kernel.modules_disabled=1`, create `/etc/systemd/system/modules-lockdown.service`:

```ini
[Unit]
Description=Lock out kernel module loading
After=systemd-modules-load.service
After=multi-user.target

[Service]
Type=oneshot
ExecStart=/sbin/sysctl -w kernel.modules_disabled=1
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

This sets `modules_disabled=1` after all boot-time modules are loaded.

---

## Appendix: i7-10700 CPU Vulnerability Status

Check your actual status:
```bash
grep -r . /sys/devices/system/cpu/vulnerabilities/
```

Expected vulnerabilities for Comet Lake (10th gen Intel):

| Vulnerability | Expected Status |
|--------------|----------------|
| Spectre v1 | Mitigation: usercopy/swapgs barriers |
| Spectre v2 | Mitigation: Enhanced IBRS + IBPB |
| Meltdown | Mitigation: PTI |
| MDS | Mitigation: Clear buffers |
| TSX Async Abort | Mitigation: TSX disabled |
| L1TF | Mitigation: PTE Inversion |
| SRBDS | Mitigation: Microcode |
| MMIO Stale Data | Mitigation: Clear buffers |
| Retbleed | Not affected (Intel) or Mitigation: IBRS |
| GDS (Gather Data Sampling) | Mitigation: Microcode |

---

## Related Reports

| Report | Topic | Status |
|--------|-------|--------|
| **25** | systemd-system.conf(5) — System-wide defaults | ✅ Complete |
| **26** | systemd.exec(5) — Per-service execution (162 options) | ✅ Complete |
| **27** | systemd.resource-control(5) — Cgroup controls (57 options) | ✅ Complete |
| **28** | Kernel cmdline + sysctl hardening (THIS REPORT) | ✅ Complete |
| **29** | Audit framework (auditd + systemd) | 📋 Next |

---

*Report 28 of the masterhq investigation series. Complete kernel boot parameter and sysctl hardening guide with ready-to-deploy configurations for the ASUS PRIME B460M-A / i7-10700 system.*
