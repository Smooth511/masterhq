# Report 29 — Linux Audit Framework: auditd Rules & systemd Integration

**Classification:** SYSTEM HARDENING — FULL REFERENCE GUIDE  
**Prepared by:** ClaudeMKII (MK2PK)  
**Report Date:** 2026-04-18  
**Sources:** audit.rules(7), auditctl(8), auditd.conf(5), CIS Benchmarks (Ubuntu 24.04), STIG guidelines  
**System:** ASUS PRIME B460M-A, Intel i7-10700 (8C/16T, 2.9GHz base / 4.8GHz boost), 16GB RAM  
**OS:** Linux Mint 22.3 Zena (Ubuntu 24.04 base)  
**Kernels:** 6.14.0-37-generic, 6.17.0-20-generic  
**Builds on:** Reports 24-28 (rootkit analysis, systemd hardening, kernel hardening)  
**Identifier:** ClaudeMKII-Seed-20260317

---

## TABLE OF CONTENTS

1. [What the Audit Framework Is](#1-what-the-audit-framework-is)
2. [Architecture and Components](#2-architecture-and-components)
3. [auditd.conf — Daemon Configuration](#3-auditdconf--daemon-configuration)
4. [Rule Types and Syntax](#4-rule-types-and-syntax)
5. [Control Rules](#5-control-rules)
6. [File/Directory Watch Rules](#6-filedirectory-watch-rules)
7. [Syscall Rules — Format and Fields](#7-syscall-rules--format-and-fields)
8. [Identity and Authentication Monitoring](#8-identity-and-authentication-monitoring)
9. [Privilege Escalation Detection](#9-privilege-escalation-detection)
10. [File Integrity Monitoring](#10-file-integrity-monitoring)
11. [Kernel Module and Boot Chain Monitoring](#11-kernel-module-and-boot-chain-monitoring)
12. [Network Configuration Monitoring](#12-network-configuration-monitoring)
13. [Time and Hostname Change Detection](#13-time-and-hostname-change-detection)
14. [Process Execution Auditing](#14-process-execution-auditing)
15. [Filesystem Permission Changes](#15-filesystem-permission-changes)
16. [Failed Access Attempts](#16-failed-access-attempts)
17. [Audit Log Management](#17-audit-log-management)
18. [systemd Integration](#18-systemd-integration)
19. [Log Analysis Tools](#19-log-analysis-tools)
20. [Complete Hardened Audit Rules for ASUS B460M-A](#20-complete-hardened-audit-rules-for-asus-b460m-a)
21. [Investigation-Specific Rules](#21-investigation-specific-rules)
22. [Appendix: Common Syscalls Reference](#appendix-common-syscalls-reference)

---

## 1. What the Audit Framework Is

The Linux Audit Framework is a kernel-level event logging system that records:
- **Syscall activity** — what processes do at the kernel interface
- **File access** — reads, writes, attribute changes to critical files
- **User actions** — logins, privilege escalation, identity changes
- **Security events** — SELinux/AppArmor denials, capability use

It operates at a lower level than application logging and **cannot be bypassed by userspace code** (unless the attacker has kernel-level access).

### Why It Matters for This Investigation

The rootkit documented in Report 24:
- Modified boot chain files (`/boot/grub/grub.cfg`, `/boot/efi/EFI/ubuntu/grub.cfg`)
- Enrolled MOK certificates
- Installed Ventoy on internal NVMe
- Replaced core libraries (`libc.so.6`, `libstdc++.so.6.0.33`, `libgcc_s.so.1` — Report 25)

**With audit rules in place**, every one of these actions would have been logged:
- File watches on `/boot/` would catch GRUB modification
- Module loading rules would catch certificate enrollment
- Library watches would catch shared library replacement
- Execution rules would catch Ventoy installation

---

## 2. Architecture and Components

```
┌─────────────────────────────────────────────┐
│                  Kernel                       │
│  ┌──────────────────────────────────────┐    │
│  │         Audit Subsystem              │    │
│  │  (receives events from all syscalls) │    │
│  └──────────────┬───────────────────────┘    │
└─────────────────┼────────────────────────────┘
                  │ netlink
                  ▼
┌─────────────────────────────┐
│         auditd              │  ← Daemon: writes events to logs
│  /var/log/audit/audit.log   │
└──────────┬──────────────────┘
           │
    ┌──────┴──────┐
    ▼             ▼
 audispd       aureport    ← Dispatcher + reporting tools
 (plugins)     ausearch
               aulast
```

| Component | Role |
|-----------|------|
| **Kernel audit subsystem** | Generates events; enabled with `audit=1` boot param (Report 28) |
| **auditd** | Userspace daemon that receives events and writes to log files |
| **auditctl** | Runtime rule management (add/delete/list rules) |
| **audit.rules** | Persistent rules loaded at boot |
| **ausearch** | Search audit logs by criteria |
| **aureport** | Generate summary reports from audit logs |
| **audispd** | Event dispatcher for plugins (syslog, remote, etc.) |

### File Locations

| File | Purpose |
|------|---------|
| `/etc/audit/auditd.conf` | Daemon configuration |
| `/etc/audit/rules.d/*.rules` | Persistent audit rules (loaded in alphabetical order) |
| `/etc/audit/audit.rules` | Compiled rules (generated from rules.d/) |
| `/var/log/audit/audit.log` | Primary audit log |
| `/etc/audit/plugins.d/` | Dispatcher plugin configs |

---

## 3. auditd.conf — Daemon Configuration

### Key Settings

| Setting | Default | Hardened | Effect |
|---------|---------|----------|--------|
| `log_file` | `/var/log/audit/audit.log` | Keep default | Log file path |
| `log_format` | `ENRICHED` | `ENRICHED` | Include resolved names (users, syscalls) |
| `log_group` | `adm` | `root` | Group that can read audit logs |
| `priority_boost` | 4 | 4 | Nice priority boost for auditd |
| `flush` | `INCREMENTAL_ASYNC` | `INCREMENTAL_ASYNC` | When to flush to disk |
| `freq` | 50 | 50 | Records between forced flushes |
| `num_logs` | 5 | 10 | Number of rotated log files to keep |
| `max_log_file` | 8 (MB) | 50 | Max log file size before rotation |
| `max_log_file_action` | `ROTATE` | `ROTATE` | Action when max size reached |
| `space_left` | 75 (MB) | 200 | Disk space threshold for warning |
| `space_left_action` | `SYSLOG` | `SYSLOG` | Action at warning threshold |
| `admin_space_left` | 50 (MB) | 100 | Critical disk space threshold |
| `admin_space_left_action` | `SUSPEND` | `HALT` | Action at critical threshold |
| `disk_full_action` | `SUSPEND` | `HALT` | Action when disk full |
| `disk_error_action` | `SUSPEND` | `HALT` | Action on disk error |

**Hardened `/etc/audit/auditd.conf`:**
```ini
log_file = /var/log/audit/audit.log
log_format = ENRICHED
log_group = root
priority_boost = 4
flush = INCREMENTAL_ASYNC
freq = 50
num_logs = 10
max_log_file = 50
max_log_file_action = ROTATE
space_left = 200
space_left_action = SYSLOG
admin_space_left = 100
admin_space_left_action = HALT
disk_full_action = HALT
disk_error_action = HALT
```

**`HALT` on disk full/error:** The system will HALT rather than lose audit events. This is the CIS/STIG recommendation for high-security systems. Use `SUSPEND` if system availability matters more than audit completeness.

---

## 4. Rule Types and Syntax

### Three Rule Types

| Type | Syntax | Purpose |
|------|--------|---------|
| **Control** | `-b`, `-D`, `-e`, `-f` | Configure audit subsystem behaviour |
| **File watch** | `-w PATH -p PERMS -k KEY` | Watch files/directories for access |
| **Syscall** | `-a ACTION,FILTER -S SYSCALL -F FIELD=VALUE -k KEY` | Monitor specific system calls |

### Rule Loading Order

Rules in `/etc/audit/rules.d/` are loaded alphabetically. Convention:
```
10-base.rules         # Buffer size, delete existing rules
20-identity.rules     # User/group monitoring
30-privilege.rules    # Privilege escalation
40-access.rules       # File access
50-network.rules      # Network changes
60-system.rules       # System configuration
70-kernel.rules       # Kernel/module changes
99-finalize.rules     # Make rules immutable
```

### Generate compiled rules:
```bash
augenrules --load
# Or manually:
auditctl -R /etc/audit/rules.d/10-base.rules
```

---

## 5. Control Rules

### 5.1 Buffer Size

```bash
-b 8192
```

Sets the kernel audit buffer to 8192 events. Increase if you see "backlog limit exceeded" messages. Report 28 also sets `audit_backlog_limit=8192` on the kernel command line for early-boot events.

### 5.2 Delete All Rules

```bash
-D
```

Always start with this — clears any runtime-added rules before loading the persistent set.

### 5.3 Failure Mode

```bash
-f 2
```

| Value | Effect |
|-------|--------|
| 0 | Silent — drop events if buffer full |
| 1 | Printk — log a message when events dropped |
| 2 | Panic — kernel panic if events cannot be logged |

**Hardening: `-f 1`** for most systems, `-f 2` for critical investigation systems where audit loss is unacceptable.

### 5.4 Immutable Rules

```bash
-e 2
```

Makes the audit configuration **immutable** — cannot be changed at runtime. Requires reboot to modify. Must be the LAST rule loaded.

**Hardening: `-e 2`** — Prevents an attacker from disabling audit rules after gaining root.

---

## 6. File/Directory Watch Rules

### Syntax

```bash
-w PATH -p PERMISSIONS -k KEY
```

| Flag | Meaning |
|------|---------|
| `-w` | Path to watch (file or directory) |
| `-p` | Permission filter: `r`ead, `w`rite, e`x`ecute, `a`ttribute change |
| `-k` | Key/tag for filtering logs |

### Key Concepts

- **Directory watches** are NOT recursive — they only watch the directory itself, not subdirectories
- **File watches** track the inode, so they survive file renames within the same filesystem
- `-p wa` (write + attribute) is the most common combination for change detection
- `-p x` watches for execution

---

## 7. Syscall Rules — Format and Fields

### Full Syntax

```bash
-a ACTION,FILTER -F FIELD=VALUE [-F ...] -S SYSCALL [-S ...] -k KEY
```

### ACTION

| Action | Effect |
|--------|--------|
| `always` | Always generate an audit record |
| `never` | Never generate (exclude rule) |

### FILTER

| Filter | When it fires |
|--------|--------------|
| `exit` | After syscall returns (most common) |
| `entry` | Before syscall executes (deprecated) |
| `task` | When new process/thread created |
| `user` | User-space events |
| `exclude` | Exclude matching events |

### Common Fields (-F)

| Field | Description | Example |
|-------|-------------|---------|
| `arch=` | Architecture | `b64` (64-bit), `b32` (32-bit) |
| `uid=` | Real UID | `uid=0` (root) |
| `euid=` | Effective UID | `euid=0` |
| `auid=` | Audit UID (login UID, survives `su`) | `auid>=1000` |
| `pid=` | Process ID | `pid=1` |
| `exe=` | Executable path | `exe=/usr/bin/sudo` |
| `path=` | File path being accessed | `path=/etc/shadow` |
| `dir=` | Directory being accessed | `dir=/etc/` |
| `key=` | Same as `-k` | `key=identity` |
| `exit=` | Syscall return value | `exit=-EACCES` |
| `success=` | Whether syscall succeeded | `success=no` |
| `perm=` | File permission filter | `perm=wa` |

### Special auid Values

| Value | Meaning |
|-------|---------|
| `auid>=1000` | Real users (not system accounts) |
| `auid!=4294967295` | Exclude unset auid (0xFFFFFFFF = -1) — processes without login session |
| `auid!=unset` | Same as above (modern syntax) |

**Always include both `arch=b64` AND `arch=b32` rules** — an attacker can use 32-bit syscalls on a 64-bit system to bypass 64-bit-only rules.

---

## 8. Identity and Authentication Monitoring

```bash
# === User/Group Identity Files ===
-w /etc/passwd -p wa -k identity
-w /etc/shadow -p wa -k identity
-w /etc/group -p wa -k identity
-w /etc/gshadow -p wa -k identity
-w /etc/security/opasswd -p wa -k identity

# === PAM Configuration ===
-w /etc/pam.d/ -p wa -k pam
-w /etc/security/ -p wa -k pam

# === Login Configuration ===
-w /etc/login.defs -p wa -k login
-w /etc/securetty -p wa -k login

# === NSS/SSSD ===
-w /etc/nsswitch.conf -p wa -k nss
-w /etc/sssd/ -p wa -k sssd

# === Login Records ===
-w /var/log/lastlog -p wa -k logins
-w /var/run/faillock/ -p wa -k logins
-w /var/log/wtmp -p wa -k logins
-w /var/log/btmp -p wa -k logins
```

---

## 9. Privilege Escalation Detection

```bash
# === Privileged Command Execution ===
-w /usr/bin/sudo -p x -k priv_cmd
-w /usr/bin/su -p x -k priv_cmd
-w /usr/bin/newgrp -p x -k priv_cmd
-w /usr/bin/chsh -p x -k priv_cmd
-w /usr/bin/chfn -p x -k priv_cmd
-w /usr/bin/gpasswd -p x -k priv_cmd
-w /usr/bin/passwd -p x -k priv_cmd

# === Sudoers ===
-w /etc/sudoers -p wa -k sudoers
-w /etc/sudoers.d/ -p wa -k sudoers

# === Setuid/Setgid Syscalls (privilege change) ===
-a always,exit -F arch=b64 -S setuid,setgid,setreuid,setregid,setresuid,setresgid -F auid>=1000 -F auid!=unset -k priv_esc
-a always,exit -F arch=b32 -S setuid,setgid,setreuid,setregid,setresuid,setresgid -F auid>=1000 -F auid!=unset -k priv_esc

# === Execve with privilege change (UID mismatch = setuid binary used) ===
-a always,exit -F arch=b64 -S execve -C uid!=euid -F euid=0 -k priv_esc_exec
-a always,exit -F arch=b32 -S execve -C uid!=euid -F euid=0 -k priv_esc_exec

# === Capability use ===
-a always,exit -F arch=b64 -S capset -k capability
-a always,exit -F arch=b32 -S capset -k capability
```

---

## 10. File Integrity Monitoring

```bash
# === Critical System Configuration ===
-w /etc/sysctl.conf -p wa -k sysctl
-w /etc/sysctl.d/ -p wa -k sysctl
-w /etc/modprobe.d/ -p wa -k modprobe
-w /etc/modules-load.d/ -p wa -k modules

# === Systemd Configuration ===
-w /etc/systemd/ -p wa -k systemd_config
-w /usr/lib/systemd/ -p wa -k systemd_lib
-w /run/systemd/system/ -p wa -k systemd_runtime

# === Cron / Scheduled Tasks ===
-w /etc/crontab -p wa -k cron
-w /etc/cron.d/ -p wa -k cron
-w /etc/cron.daily/ -p wa -k cron
-w /etc/cron.hourly/ -p wa -k cron
-w /etc/cron.weekly/ -p wa -k cron
-w /etc/cron.monthly/ -p wa -k cron
-w /var/spool/cron/ -p wa -k cron

# === SSH Configuration ===
-w /etc/ssh/ -p wa -k ssh
-w /root/.ssh/ -p wa -k ssh

# === Shell Configuration (persistence via profile) ===
-w /etc/profile -p wa -k shell_config
-w /etc/profile.d/ -p wa -k shell_config
-w /etc/bashrc -p wa -k shell_config
-w /etc/bash.bashrc -p wa -k shell_config
-w /etc/environment -p wa -k shell_config
-w /etc/shells -p wa -k shell_config

# === Shared Libraries ===
-w /etc/ld.so.conf -p wa -k lib_config
-w /etc/ld.so.conf.d/ -p wa -k lib_config
-w /etc/ld.so.preload -p wa -k lib_preload
```

---

## 11. Kernel Module and Boot Chain Monitoring

**This section directly addresses the rootkit attack chain from Report 24.**

```bash
# === Boot Chain ===
-w /boot/ -p wa -k boot
-w /boot/grub/ -p wa -k grub
-w /boot/efi/ -p wa -k efi
-w /boot/efi/EFI/ -p wa -k efi

# === GRUB Configuration ===
-w /etc/default/grub -p wa -k grub_config
-w /boot/grub/grub.cfg -p wa -k grub_config

# === Kernel Module Loading ===
-w /sbin/insmod -p x -k module_load
-w /sbin/rmmod -p x -k module_unload
-w /sbin/modprobe -p x -k module_load
-w /usr/bin/kmod -p x -k module_load

# === Module loading syscalls ===
-a always,exit -F arch=b64 -S init_module,finit_module -k module_load
-a always,exit -F arch=b32 -S init_module,finit_module -k module_load
-a always,exit -F arch=b64 -S delete_module -k module_unload
-a always,exit -F arch=b32 -S delete_module -k module_unload

# === MOK (Machine Owner Key) — the rootkit enrolled CN=grub here ===
-w /var/lib/shim-signed/ -p wa -k mok
-w /var/lib/dkms/ -p wa -k dkms

# === Kernel image and initrd ===
-w /boot/vmlinuz -p wa -k kernel_image
-w /boot/initrd.img -p wa -k initrd

# === kexec (load new kernel from userspace) ===
-a always,exit -F arch=b64 -S kexec_load,kexec_file_load -k kexec
-a always,exit -F arch=b32 -S kexec_load -k kexec

# === Seccomp ===
-a always,exit -F arch=b64 -S seccomp -k seccomp
```

---

## 12. Network Configuration Monitoring

```bash
# === Network Configuration Files ===
-w /etc/hosts -p wa -k network_config
-w /etc/hostname -p wa -k network_config
-w /etc/network/ -p wa -k network_config
-w /etc/NetworkManager/ -p wa -k network_config
-w /etc/netplan/ -p wa -k network_config
-w /etc/resolv.conf -p wa -k dns_config

# === Firewall Rules ===
-w /etc/nftables.conf -p wa -k firewall
-w /etc/ufw/ -p wa -k firewall

# === Network syscalls (socket creation by non-root) ===
# WARNING: Very noisy. Use only during investigation.
# -a always,exit -F arch=b64 -S socket -F a0=2 -k ipv4_socket
# -a always,exit -F arch=b64 -S socket -F a0=10 -k ipv6_socket
# -a always,exit -F arch=b64 -S connect -k network_connect
```

---

## 13. Time and Hostname Change Detection

```bash
# === Time changes (CIS requirement) ===
-a always,exit -F arch=b64 -S adjtimex,settimeofday,clock_settime -k time_change
-a always,exit -F arch=b32 -S adjtimex,settimeofday,clock_settime,stime -k time_change
-w /etc/localtime -p wa -k time_change

# === Hostname changes ===
-a always,exit -F arch=b64 -S sethostname,setdomainname -k hostname_change
-a always,exit -F arch=b32 -S sethostname,setdomainname -k hostname_change
-w /etc/hostname -p wa -k hostname_change
-w /etc/hosts -p wa -k hostname_change
```

---

## 14. Process Execution Auditing

```bash
# === All process execution (WARNING: extremely noisy, use sparingly) ===
# -a always,exit -F arch=b64 -S execve -k exec
# -a always,exit -F arch=b32 -S execve -k exec

# === Root process execution ===
-a always,exit -F arch=b64 -S execve -F euid=0 -k root_exec
-a always,exit -F arch=b32 -S execve -F euid=0 -k root_exec

# === Specific suspicious binaries ===
-w /usr/bin/wget -p x -k suspicious_download
-w /usr/bin/curl -p x -k suspicious_download
-w /usr/bin/nc -p x -k suspicious_tool
-w /usr/bin/ncat -p x -k suspicious_tool
-w /usr/bin/nmap -p x -k suspicious_tool
-w /usr/bin/tcpdump -p x -k suspicious_tool
-w /usr/bin/wireshark -p x -k suspicious_tool
-w /usr/sbin/iptables -p x -k firewall_tool
-w /usr/sbin/nft -p x -k firewall_tool

# === Package management ===
-w /usr/bin/dpkg -p x -k package_mgmt
-w /usr/bin/apt -p x -k package_mgmt
-w /usr/bin/apt-get -p x -k package_mgmt
-w /usr/bin/snap -p x -k package_mgmt
```

---

## 15. Filesystem Permission Changes

```bash
# === chmod/chown/chattr ===
-a always,exit -F arch=b64 -S chmod,fchmod,fchmodat -F auid>=1000 -F auid!=unset -k perm_mod
-a always,exit -F arch=b32 -S chmod,fchmod,fchmodat -F auid>=1000 -F auid!=unset -k perm_mod

-a always,exit -F arch=b64 -S chown,fchown,fchownat,lchown -F auid>=1000 -F auid!=unset -k owner_mod
-a always,exit -F arch=b32 -S chown,fchown,fchownat,lchown -F auid>=1000 -F auid!=unset -k owner_mod

# === Extended attributes ===
-a always,exit -F arch=b64 -S setxattr,lsetxattr,fsetxattr,removexattr,lremovexattr,fremovexattr -F auid>=1000 -F auid!=unset -k xattr_mod
-a always,exit -F arch=b32 -S setxattr,lsetxattr,fsetxattr,removexattr,lremovexattr,fremovexattr -F auid>=1000 -F auid!=unset -k xattr_mod
```

---

## 16. Failed Access Attempts

```bash
# === Unsuccessful file access ===
-a always,exit -F arch=b64 -S open,openat,creat,truncate,ftruncate -F exit=-EACCES -F auid>=1000 -F auid!=unset -k access_denied
-a always,exit -F arch=b64 -S open,openat,creat,truncate,ftruncate -F exit=-EPERM -F auid>=1000 -F auid!=unset -k access_denied
-a always,exit -F arch=b32 -S open,openat,creat,truncate,ftruncate -F exit=-EACCES -F auid>=1000 -F auid!=unset -k access_denied
-a always,exit -F arch=b32 -S open,openat,creat,truncate,ftruncate -F exit=-EPERM -F auid>=1000 -F auid!=unset -k access_denied

# === Unsuccessful file deletion ===
-a always,exit -F arch=b64 -S unlink,unlinkat,rename,renameat -F exit=-EACCES -F auid>=1000 -F auid!=unset -k delete_denied
-a always,exit -F arch=b64 -S unlink,unlinkat,rename,renameat -F exit=-EPERM -F auid>=1000 -F auid!=unset -k delete_denied
```

---

## 17. Audit Log Management

### Log Rotation

Auditd manages its own rotation (NOT logrotate). Configure in `auditd.conf`:
```ini
max_log_file = 50        # MB per file
num_logs = 10            # Keep 10 rotated files
max_log_file_action = ROTATE
```

### Protecting Audit Logs

```bash
# Watch the audit system itself
-w /etc/audit/ -p wa -k audit_config
-w /var/log/audit/ -p wa -k audit_log
-w /etc/libaudit.conf -p wa -k audit_config
-w /etc/audisp/ -p wa -k audit_config

# Watch auditctl and auditd binaries
-w /sbin/auditctl -p x -k audit_tool
-w /sbin/auditd -p x -k audit_tool
-w /usr/sbin/augenrules -p x -k audit_tool
```

### Centralised Logging

For remote log shipping, configure `/etc/audit/plugins.d/au-remote.conf`:
```ini
active = yes
direction = out
path = /sbin/audisp-remote
type = always
format = string
```

---

## 18. systemd Integration

### 18.1 Boot Parameter (Report 28)

```bash
# In GRUB_CMDLINE_LINUX:
audit=1 audit_backlog_limit=8192
```

### 18.2 auditd.service

auditd runs as a systemd service but is special:
- It CANNOT be managed by `systemctl stop` (to prevent attackers from stopping it)
- Use `service auditd stop` (goes through init script that checks for immutable rules)
- Restart: `service auditd restart`
- Status: `systemctl status auditd`

### 18.3 systemd Journal Integration

systemd-journald can capture audit events alongside regular journal entries:

```ini
# /etc/systemd/journald.conf
[Journal]
Audit=yes              # Forward audit messages to journal
```

This gives you audit events in BOTH `/var/log/audit/audit.log` AND the journal, allowing:
```bash
journalctl _TRANSPORT=audit
```

### 18.4 Per-Service Audit Interaction

From Report 26 (`systemd.exec(5)`):
- `SystemCallLog=` — logs specific syscalls via seccomp (lighter weight than auditd)
- `LogExtraFields=` — adds custom journal fields
- `AuditBurstLimit=`/`AuditRateLimitIntervalSec=` — rate limit audit events per service (Report 25)

These complement auditd but don't replace it.

---

## 19. Log Analysis Tools

### 19.1 ausearch — Search Audit Logs

```bash
# Search by key
ausearch -k identity

# Search by time
ausearch -ts today -te now -k priv_esc

# Search by user
ausearch -ua 1000

# Search by syscall
ausearch -sc execve

# Search by success/failure
ausearch -sv no -k access_denied

# Search by file
ausearch -f /etc/shadow

# Combine criteria
ausearch -k boot -ts "04/17/2026" -te "04/18/2026"
```

### 19.2 aureport — Summary Reports

```bash
# Summary of all events
aureport --summary

# Authentication report
aureport -au

# Login report
aureport -l

# Failed events
aureport --failed

# File access report
aureport -f

# Executable report
aureport -x

# Key-based summary
aureport -k --summary

# Anomaly report
aureport --anomaly
```

### 19.3 aulast — Login History from Audit

```bash
aulast              # Similar to 'last' but from audit log
aulast --bad        # Failed logins only
```

---

## 20. Complete Hardened Audit Rules for ASUS B460M-A

Save as `/etc/audit/rules.d/99-hardened.rules`:

```bash
# =============================================================
# HARDENED AUDIT RULES — ASUS PRIME B460M-A / i7-10700
# Linux Mint 22.3 Zena — Kernels 6.14.0-37 / 6.17.0-20
# CIS Benchmark + Investigation-specific rules
# =============================================================

# === CONTROL RULES ===
-D
-b 8192
-f 1

# === IDENTITY & AUTHENTICATION ===
-w /etc/passwd -p wa -k identity
-w /etc/shadow -p wa -k identity
-w /etc/group -p wa -k identity
-w /etc/gshadow -p wa -k identity
-w /etc/security/opasswd -p wa -k identity
-w /etc/pam.d/ -p wa -k pam
-w /etc/login.defs -p wa -k login
-w /etc/securetty -p wa -k login
-w /var/log/lastlog -p wa -k logins
-w /var/run/faillock/ -p wa -k logins
-w /var/log/wtmp -p wa -k logins
-w /var/log/btmp -p wa -k logins

# === PRIVILEGE ESCALATION ===
-w /usr/bin/sudo -p x -k priv_cmd
-w /usr/bin/su -p x -k priv_cmd
-w /usr/bin/passwd -p x -k priv_cmd
-w /usr/bin/newgrp -p x -k priv_cmd
-w /etc/sudoers -p wa -k sudoers
-w /etc/sudoers.d/ -p wa -k sudoers
-a always,exit -F arch=b64 -S setuid,setgid,setreuid,setregid,setresuid,setresgid -F auid>=1000 -F auid!=unset -k priv_esc
-a always,exit -F arch=b32 -S setuid,setgid,setreuid,setregid,setresuid,setresgid -F auid>=1000 -F auid!=unset -k priv_esc
-a always,exit -F arch=b64 -S execve -C uid!=euid -F euid=0 -k priv_esc_exec
-a always,exit -F arch=b32 -S execve -C uid!=euid -F euid=0 -k priv_esc_exec

# === BOOT CHAIN (critical — rootkit detection) ===
-w /boot/ -p wa -k boot
-w /boot/grub/ -p wa -k grub
-w /boot/efi/ -p wa -k efi
-w /etc/default/grub -p wa -k grub_config
-w /boot/grub/grub.cfg -p wa -k grub_config

# === KERNEL MODULES ===
-w /sbin/insmod -p x -k module_load
-w /sbin/rmmod -p x -k module_unload
-w /sbin/modprobe -p x -k module_load
-w /usr/bin/kmod -p x -k module_load
-a always,exit -F arch=b64 -S init_module,finit_module -k module_load
-a always,exit -F arch=b32 -S init_module,finit_module -k module_load
-a always,exit -F arch=b64 -S delete_module -k module_unload
-a always,exit -F arch=b32 -S delete_module -k module_unload
-a always,exit -F arch=b64 -S kexec_load,kexec_file_load -k kexec

# === MOK KEYS ===
-w /var/lib/shim-signed/ -p wa -k mok
-w /var/lib/dkms/ -p wa -k dkms

# === SYSTEM CONFIGURATION ===
-w /etc/sysctl.conf -p wa -k sysctl
-w /etc/sysctl.d/ -p wa -k sysctl
-w /etc/modprobe.d/ -p wa -k modprobe
-w /etc/systemd/ -p wa -k systemd_config
-w /etc/ssh/ -p wa -k ssh
-w /root/.ssh/ -p wa -k ssh

# === SHARED LIBRARIES (rootkit detection) ===
-w /etc/ld.so.conf -p wa -k lib_config
-w /etc/ld.so.conf.d/ -p wa -k lib_config
-w /etc/ld.so.preload -p wa -k lib_preload

# === SHELL PERSISTENCE ===
-w /etc/profile -p wa -k shell_config
-w /etc/profile.d/ -p wa -k shell_config
-w /etc/bash.bashrc -p wa -k shell_config
-w /etc/environment -p wa -k shell_config
-w /etc/shells -p wa -k shell_config

# === SCHEDULED TASKS ===
-w /etc/crontab -p wa -k cron
-w /etc/cron.d/ -p wa -k cron
-w /etc/cron.daily/ -p wa -k cron
-w /etc/cron.hourly/ -p wa -k cron
-w /var/spool/cron/ -p wa -k cron

# === NETWORK CONFIGURATION ===
-w /etc/hosts -p wa -k network_config
-w /etc/hostname -p wa -k network_config
-w /etc/resolv.conf -p wa -k dns_config
-w /etc/NetworkManager/ -p wa -k network_config
-w /etc/netplan/ -p wa -k network_config
-w /etc/nftables.conf -p wa -k firewall
-w /etc/ufw/ -p wa -k firewall

# === TIME CHANGES ===
-a always,exit -F arch=b64 -S adjtimex,settimeofday,clock_settime -k time_change
-a always,exit -F arch=b32 -S adjtimex,settimeofday,clock_settime,stime -k time_change
-w /etc/localtime -p wa -k time_change

# === HOSTNAME CHANGES ===
-a always,exit -F arch=b64 -S sethostname,setdomainname -k hostname_change
-a always,exit -F arch=b32 -S sethostname,setdomainname -k hostname_change

# === ROOT COMMAND EXECUTION ===
-a always,exit -F arch=b64 -S execve -F euid=0 -k root_exec
-a always,exit -F arch=b32 -S execve -F euid=0 -k root_exec

# === PERMISSION CHANGES ===
-a always,exit -F arch=b64 -S chmod,fchmod,fchmodat -F auid>=1000 -F auid!=unset -k perm_mod
-a always,exit -F arch=b32 -S chmod,fchmod,fchmodat -F auid>=1000 -F auid!=unset -k perm_mod
-a always,exit -F arch=b64 -S chown,fchown,fchownat,lchown -F auid>=1000 -F auid!=unset -k owner_mod
-a always,exit -F arch=b32 -S chown,fchown,fchownat,lchown -F auid>=1000 -F auid!=unset -k owner_mod

# === FAILED ACCESS ===
-a always,exit -F arch=b64 -S open,openat,creat,truncate,ftruncate -F exit=-EACCES -F auid>=1000 -F auid!=unset -k access_denied
-a always,exit -F arch=b64 -S open,openat,creat,truncate,ftruncate -F exit=-EPERM -F auid>=1000 -F auid!=unset -k access_denied
-a always,exit -F arch=b32 -S open,openat,creat,truncate,ftruncate -F exit=-EACCES -F auid>=1000 -F auid!=unset -k access_denied
-a always,exit -F arch=b32 -S open,openat,creat,truncate,ftruncate -F exit=-EPERM -F auid>=1000 -F auid!=unset -k access_denied

# === SUSPICIOUS TOOLS ===
-w /usr/bin/wget -p x -k suspicious_download
-w /usr/bin/curl -p x -k suspicious_download
-w /usr/bin/nc -p x -k suspicious_tool
-w /usr/bin/ncat -p x -k suspicious_tool
-w /usr/bin/nmap -p x -k suspicious_tool

# === PACKAGE MANAGEMENT ===
-w /usr/bin/dpkg -p x -k package_mgmt
-w /usr/bin/apt -p x -k package_mgmt
-w /usr/bin/apt-get -p x -k package_mgmt

# === AUDIT SYSTEM SELF-PROTECTION ===
-w /etc/audit/ -p wa -k audit_config
-w /var/log/audit/ -p wa -k audit_log
-w /sbin/auditctl -p x -k audit_tool
-w /sbin/auditd -p x -k audit_tool

# === MAKE RULES IMMUTABLE (must be last) ===
-e 2
```

### Deploy

```bash
# Copy rules
sudo cp 99-hardened.rules /etc/audit/rules.d/

# Load rules
sudo augenrules --load

# Verify
sudo auditctl -l | wc -l    # Should show ~80+ rules
sudo auditctl -s             # Status should show enabled=2 (immutable)
```

---

## 21. Investigation-Specific Rules

These rules are tailored to the rootkit attack vectors discovered in Reports 18 and 24. Enable during active investigation, disable in normal operation (they're noisy).

```bash
# === INVESTIGATION MODE — ROOTKIT DETECTION ===
# Save as /etc/audit/rules.d/95-investigation.rules
# Remove when investigation complete

# === All execve (every process execution) ===
-a always,exit -F arch=b64 -S execve -k exec_all
-a always,exit -F arch=b32 -S execve -k exec_all

# === Mount operations (Ventoy uses dm + mount) ===
-a always,exit -F arch=b64 -S mount,umount2 -k mount_op
-a always,exit -F arch=b32 -S mount,umount,umount2 -k mount_op

# === Device mapper operations ===
-a always,exit -F arch=b64 -S ioctl -F a1=0xC138FD00 -k dm_ioctl
# (0xC138FD00 = DM_DEV_CREATE, varies by kernel)

# === /dev/nvme access (rootkit was on nvme1n1) ===
-w /dev/nvme0 -p rw -k nvme_access
-w /dev/nvme1 -p rw -k nvme_access

# === Casper/overlay filesystem ===
-w /cdrom/ -p wa -k casper
-w /rofs/ -p wa -k casper

# === Socket creation (detect C2 connections) ===
-a always,exit -F arch=b64 -S socket -F a0=2 -k ipv4_socket_create
-a always,exit -F arch=b64 -S socket -F a0=10 -k ipv6_socket_create
-a always,exit -F arch=b64 -S connect -k network_connect

# === All file deletions by any user ===
-a always,exit -F arch=b64 -S unlink,unlinkat,rename,renameat,renameat2 -k file_delete
-a always,exit -F arch=b32 -S unlink,unlinkat,rename,renameat -k file_delete

# === ptrace (debugger/injector detection) ===
-a always,exit -F arch=b64 -S ptrace -k ptrace_detect
-a always,exit -F arch=b32 -S ptrace -k ptrace_detect

# === Shared library loading (LD_PRELOAD attacks) ===
-a always,exit -F arch=b64 -S openat -F dir=/usr/lib -F perm=r -k lib_load
-a always,exit -F arch=b64 -S openat -F dir=/lib -F perm=r -k lib_load
```

---

## Appendix: Common Syscalls Reference

| Syscall | Purpose | Audit Key |
|---------|---------|-----------|
| `execve` | Execute program | `exec`, `priv_esc_exec` |
| `open`, `openat` | Open file | `access_denied` |
| `creat` | Create file | `access_denied` |
| `unlink`, `unlinkat` | Delete file | `file_delete` |
| `rename`, `renameat` | Rename file | `file_delete` |
| `chmod`, `fchmod`, `fchmodat` | Change permissions | `perm_mod` |
| `chown`, `fchown`, `fchownat`, `lchown` | Change ownership | `owner_mod` |
| `setxattr`, `removexattr` | Extended attributes | `xattr_mod` |
| `mount`, `umount2` | Mount/unmount | `mount_op` |
| `init_module`, `finit_module` | Load kernel module | `module_load` |
| `delete_module` | Unload kernel module | `module_unload` |
| `kexec_load`, `kexec_file_load` | Load new kernel | `kexec` |
| `setuid`, `setgid`, `setresuid`, `setresgid` | Change credentials | `priv_esc` |
| `capset` | Change capabilities | `capability` |
| `adjtimex`, `settimeofday`, `clock_settime` | Change time | `time_change` |
| `sethostname`, `setdomainname` | Change hostname | `hostname_change` |
| `socket`, `connect` | Network operations | `network_*` |
| `ptrace` | Debug/trace process | `ptrace_detect` |
| `seccomp` | Install seccomp filter | `seccomp` |

---

## Related Reports

| Report | Topic | Status |
|--------|-------|--------|
| **25** | systemd-system.conf(5) — System-wide defaults | ✅ Complete |
| **26** | systemd.exec(5) — Per-service execution (162 options) | ✅ Complete |
| **27** | systemd.resource-control(5) — Cgroup controls (57 options) | ✅ Complete |
| **28** | Kernel cmdline + sysctl hardening | ✅ Complete |
| **29** | Audit framework — auditd + systemd (THIS REPORT) | ✅ Complete |

---

*Report 29 of the masterhq investigation series. Complete Linux audit framework guide with CIS-aligned rules, investigation-specific detection rules targeting the documented rootkit attack vectors, and ready-to-deploy configurations for the ASUS PRIME B460M-A / i7-10700 system.*
