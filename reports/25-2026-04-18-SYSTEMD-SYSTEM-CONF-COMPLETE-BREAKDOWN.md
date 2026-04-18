# Report 25 — systemd-system.conf(5): Complete Configuration Breakdown

**Classification:** SYSTEM HARDENING — FULL REFERENCE GUIDE  
**Prepared by:** ClaudeMKII (MK2PK)  
**Report Date:** 2026-04-18  
**Sources:** https://man.archlinux.org/man/systemd-system.conf.5 (systemd 260.1), kernel docs, capabilities(7), systemd.exec(5)  
**System:** ASUS PRIME B460M-A, Intel i7-10700 (8C/16T, 2.9GHz base / 4.8GHz boost), 16GB RAM  
**OS:** Linux Mint 22.3 Zena (Ubuntu 24.04 base)  
**Kernels:** 6.14.0-37-generic, 6.17.0-20-generic  
**Builds on:** Reports 24, 25 (rootkit/boot chain analysis — security context)  
**Identifier:** ClaudeMKII-Seed-20260317

---

## TABLE OF CONTENTS

1. [What This File Is](#1-what-this-file-is)
2. [File Locations and Precedence](#2-file-locations-and-precedence)
3. [Basic Manager Options](#3-basic-manager-options)
4. [CtrlAltDel and Status](#4-ctrlaltdel-and-status)
5. [Resource Management — Timer and CPU](#5-resource-management--timer-and-cpu)
6. [Resource Management — NUMA](#6-resource-management--numa)
7. [Resource Management — Accounting](#7-resource-management--accounting)
8. [Resource Management — Tasks and Limits](#8-resource-management--tasks-and-limits)
9. [Resource Management — OOM](#9-resource-management--oom)
10. [Resource Management — Memory Pressure](#10-resource-management--memory-pressure)
11. [Hardware Watchdog](#11-hardware-watchdog)
12. [Security — Capabilities](#12-security--capabilities)
13. [Security — Privilege and System Protection](#13-security--privilege-and-system-protection)
14. [Security — System Call Architecture Filtering](#14-security--system-call-architecture-filtering)
15. [Security — SMACK and SUID/SGID](#15-security--smack-and-suidsgid)
16. [Timeouts and Rate Limits](#16-timeouts-and-rate-limits)
17. [Environment Variables](#17-environment-variables)
18. [Specifiers Reference](#18-specifiers-reference)
19. [Deprecated Options](#19-deprecated-options)
20. [ASUS B460M-A / i7-10700 — Complete Hardened Configuration](#20-asus-b460m-a--i7-10700--complete-hardened-configuration)
21. [Kernel Command Line Overrides](#21-kernel-command-line-overrides)
22. [Related Man Pages — What to Read Next](#22-related-man-pages--what-to-read-next)

---

## 1. What This File Is

`systemd-system.conf` is the **master configuration file for PID 1** — the systemd service manager. Every setting in this file controls how the **system manager itself behaves** and sets **defaults that cascade to every service, timer, socket, and process** on the system.

### Two Modes

| Mode | Config File | When |
|------|-------------|------|
| **System instance** (PID 1) | `/etc/systemd/system.conf` | Boot — runs as root, manages everything |
| **User instance** | `~/.config/systemd/user.conf` | Login — per-user service manager |

### What This Controls

- How the system logs, crashes, and recovers
- CPU affinity, NUMA policy, timer accuracy for **all processes**
- Hardware watchdog behavior (auto-reboot on hang)
- Capability bounding sets (what privileges ANY process can ever have)
- System call architecture filtering (block 32-bit execution system-wide)
- Default resource limits for all services (file descriptors, memory locks, CPU time, etc.)
- OOM killer behavior
- Default timeouts for all services
- Environment variables for the manager and all children

### Why This Matters For Your System

With the rootkit activity documented in Reports 18-24, this file is **ground zero for system hardening**. Every default here either helps or hinders an attacker. The rootkit boots via Ventoy → casper → live environment — which means the systemd configuration at boot time defines the attack surface.

---

## 2. File Locations and Precedence

### Load Order (first found wins for main config)

| Priority | Path | Who Owns It |
|----------|------|-------------|
| 1 (highest) | `/etc/systemd/system.conf` | **You** — local admin |
| 2 | `/run/systemd/system.conf` | Runtime (tmpfs, gone on reboot) |
| 3 | `/usr/local/lib/systemd/system.conf` | Local packages |
| 4 (lowest) | `/usr/lib/systemd/system.conf` | Distro vendor default |

### Drop-in Directories (override main config — higher precedence)

Drop-ins are read from **all** of these, merged in lexicographic filename order:

| Path | Purpose | Recommended Number Range |
|------|---------|-------------------------|
| `/usr/lib/systemd/system.conf.d/*.conf` | Vendor/distro defaults | 10-40 |
| `/usr/local/lib/systemd/system.conf.d/*.conf` | Local packages | 10-40 |
| `/run/systemd/system.conf.d/*.conf` | Runtime overrides | 60-90 |
| `/etc/systemd/system.conf.d/*.conf` | **Your overrides** | 60-90 |

### Key Rules

- **Last value wins** for single-value options (across sorted filenames)
- **Lists accumulate** for list-value options
- Drop-ins **always override** main config file
- To disable a vendor config: symlink it to `/dev/null` in `/etc/`
- **⚠️ /usr/local/ may not be available during early boot** if it's a separate partition

### ASUS B460M-A Implication

Your hardened settings go in `/etc/systemd/system.conf.d/90-hardened.conf`. The `90-` prefix ensures your settings override everything else. Never edit the vendor file directly — if an update replaces `/usr/lib/systemd/system.conf`, your drop-in survives.

---

## 3. Basic Manager Options

These control fundamental PID 1 behavior. All are in the `[Manager]` section.

### LogLevel=

| | |
|---|---|
| **What it does** | Sets the log verbosity for the system manager |
| **Values** | `emerg`, `alert`, `crit`, `err`, `warning`, `notice`, `info`, `debug` |
| **Default** | `info` |
| **Kernel cmdline** | `systemd.log_level=` |
| **Recommendation** | `info` for normal use. `debug` when investigating. On your system with active threats: `debug` during investigation, `info` after hardening |

### LogTarget=

| | |
|---|---|
| **What it does** | Where PID 1 sends its own log messages |
| **Values** | `console`, `journal`, `kmsg`, `journal-or-kmsg`, `null` |
| **Default** | `journal-or-kmsg` |
| **Kernel cmdline** | `systemd.log_target=` |
| **Recommendation** | `journal-or-kmsg` — ensures logs reach the journal AND kernel ring buffer. If journal is compromised, kmsg is a second path. With your rootkit situation, **never set to `null`** |

### LogColor=

| | |
|---|---|
| **What it does** | Enables/disables ANSI color in log output on the console |
| **Values** | `yes`, `no` |
| **Default** | `yes` |
| **Kernel cmdline** | `systemd.log_color=` |
| **Recommendation** | `yes` — visual distinction helps when watching boot on screen |

### LogLocation=

| | |
|---|---|
| **What it does** | Includes code location (source file + line number) in log messages |
| **Values** | `yes`, `no` |
| **Default** | `no` |
| **Kernel cmdline** | `systemd.log_location=` |
| **Recommendation** | `no` for production. `yes` when debugging systemd itself |

### LogTime=

| | |
|---|---|
| **What it does** | Prefixes log messages with a timestamp |
| **Values** | `yes`, `no` |
| **Default** | `no` |
| **Kernel cmdline** | `systemd.log_time=` |
| **Recommendation** | `yes` — timestamps on console log are critical for forensics. When you're watching boot output, timestamps tell you exactly when events happen |

### DumpCore=

| | |
|---|---|
| **What it does** | Controls whether the system manager (PID 1) dumps core on crash |
| **Values** | `yes`, `no` |
| **Default** | `yes` |
| **Kernel cmdline** | `systemd.dump_core` |
| **Recommendation** | `yes` — core dumps from PID 1 are critical forensic evidence. Your report 25 (GNU Binary Reconstruction) already showed how core dumps revealed deleted libraries. **Never disable on a system under investigation** |

### CrashChangeVT=

| | |
|---|---|
| **What it does** | Switches to a specific virtual terminal on PID 1 crash |
| **Values** | `yes`/`no` or a VT number (1-63) |
| **Default** | `no` |
| **Kernel cmdline** | `systemd.crash_vt` |
| **Recommendation** | `yes` or `1` — if PID 1 crashes, you want to see the crash output on a visible terminal, not hidden behind a GUI login screen |

### CrashShell=

| | |
|---|---|
| **What it does** | Spawns a root shell on PID 1 crash |
| **Values** | `yes`, `no` |
| **Default** | `no` |
| **Kernel cmdline** | `systemd.crash_shell` |
| **⚠️ SECURITY RISK** | This spawns an **unauthenticated root shell** on the console |
| **Recommendation** | **`no`** on any system with physical access concerns. On your ASUS desktop for investigation: `yes` ONLY if you're physically present and investigating. For hardened production: **always `no`** |

### CrashAction=

| | |
|---|---|
| **What it does** | What to do when PID 1 crashes |
| **Values** | `freeze`, `reboot`, `poweroff` |
| **Default** | `freeze` |
| **Kernel cmdline** | `systemd.crash_action` |
| **Recommendation** | `freeze` for investigation (preserves memory state). `reboot` for production resilience. On your system: **`freeze`** — if PID 1 crashes, you want to examine the state, not lose it to a reboot |

### ShowStatus=

| | |
|---|---|
| **What it does** | Shows unit status changes during boot on console |
| **Values** | `yes`, `no`, `auto`, `error` |
| **Default** | `yes` |
| **Kernel cmdline** | `systemd.show_status` |
| **Recommendation** | `yes` — you want to see every service start/stop/fail during boot. `error` is also good — only shows failures. On your system: **`yes`** because you're watching boot behavior for anomalies |

### DefaultStandardOutput=

| | |
|---|---|
| **What it does** | Where stdout of services goes by default |
| **Values** | `inherit`, `null`, `tty`, `journal`, `journal+console`, `kmsg`, `kmsg+console` |
| **Default** | `journal` |
| **Recommendation** | `journal` — all service output captured in the journal for forensics |

### DefaultStandardError=

| | |
|---|---|
| **What it does** | Where stderr of services goes by default |
| **Values** | Same as DefaultStandardOutput |
| **Default** | `inherit` (inherits from DefaultStandardOutput) |
| **Recommendation** | `inherit` — follows stdout into the journal |

---

## 4. CtrlAltDel and Status

### CtrlAltDelBurstAction=

| | |
|---|---|
| **What it does** | Action when Ctrl+Alt+Del is pressed 7+ times in 2 seconds |
| **Values** | `reboot-force`, `poweroff-force`, `reboot-immediate`, `poweroff-immediate`, `none` |
| **Default** | `reboot-force` |
| **Added** | systemd 232 |
| **Recommendation** | `none` — disable the panic reboot. An attacker (or malware) that can inject keyboard events could trigger forced reboots. On your system: **`none`**. You have physical access, you can use the power button |

### StatusUnitFormat=

| | |
|---|---|
| **What it does** | How unit names appear in boot status messages |
| **Values** | `name` (e.g. `systemd-journald.service`), `description` (e.g. `Journal Logging Service`), `combined` (both) |
| **Default** | `name` |
| **Added** | systemd 243 |
| **Recommendation** | `combined` — gives you both the technical name and human description. Makes boot output more informative when watching for anomalies |

### DefaultTimerAccuracySec=

| | |
|---|---|
| **What it does** | Default accuracy for all timer units (how much they can be delayed to batch wake-ups) |
| **Values** | Time span (e.g. `1min`, `5s`, `100ms`) |
| **Default** | `1min` |
| **Added** | systemd 212 |
| **Recommendation** | `1min` is fine for desktop. Lower values (e.g. `1s`) increase precision but consume more power/CPU from more frequent wake-ups. For your i7-10700 desktop: **`1min`** unless you need precise timer behavior for monitoring |

---

## 5. Resource Management — Timer and CPU

### TimerSlackNSec=

| | |
|---|---|
| **What it does** | Sets timer slack for PID 1, inherited by ALL processes |
| **Values** | Integer in nanoseconds (without unit suffix) or time span with suffix |
| **Default** | Unset (kernel default, typically 50μs) |
| **Added** | systemd 198 |
| **How it works** | Timer slack allows the kernel to coalesce timer events. Higher = more batching = less power, lower = more precise = more wake-ups |
| **Recommendation** | Leave default for desktop. For security monitoring that needs precise timers: `50000` (50μs). Your i7-10700 has plenty of power — don't sacrifice precision for negligible power savings |

### CPUAffinity=

| | |
|---|---|
| **What it does** | Pins PID 1 and all child processes to specific CPU cores |
| **Values** | List of CPU indices or ranges (e.g. `0 1 2-3`, `0-7`, `0,2,4,6`) |
| **Default** | Empty (all CPUs available) |
| **Added** | systemd 198 |
| **Can be overridden** | Per-unit via `CPUAffinity=` in unit files |

#### Your i7-10700 CPU Layout

| Cores | Threads | Index Range |
|-------|---------|-------------|
| 8 physical | 16 logical (HT) | 0-15 |

#### Affinity Strategies

| Strategy | Setting | Use Case |
|----------|---------|----------|
| All cores | *(empty/default)* | Normal operation |
| Performance cores only | `0-7` | Pin to physical cores, avoid HT threads |
| Isolate for monitoring | `0-13` with audit/monitoring pinned to `14-15` | Reserve 2 threads for security tools |
| Restrict PID 1 | `0-1` | Limit PID 1 to cores 0-1, free others for services |

**Recommendation:** Default (all cores). Only pin if you're running dedicated monitoring tools and want guaranteed CPU time for them. Unit-level affinity is better for individual services.

---

## 6. Resource Management — NUMA

### NUMAPolicy=

| | |
|---|---|
| **What it does** | Sets NUMA memory allocation policy for PID 1 and default for all children |
| **Values** | `default`, `preferred`, `bind`, `interleave`, `local` |
| **Default** | `default` |
| **Added** | systemd 243 |
| **Can be overridden** | Per-unit |

### NUMAMask=

| | |
|---|---|
| **What it does** | Which NUMA nodes to apply the policy to |
| **Values** | Node list/ranges |
| **Default** | Empty |
| **Added** | systemd 243 |

#### ASUS B460M-A NUMA Relevance

**Your system has ONE NUMA node** (single-socket i7-10700). NUMA settings are **irrelevant** for your hardware — they only matter for multi-socket servers with multiple physical memory controllers.

**Recommendation:** Leave both at defaults. Don't touch. No benefit on single-socket.

---

## 7. Resource Management — Accounting

These control whether systemd tracks resource usage per-unit (cgroup accounting).

### DefaultMemoryAccounting=

| | |
|---|---|
| **What it does** | Enables memory usage tracking per-unit via cgroups |
| **Default** | `yes` |
| **Added** | systemd 211 |
| **Recommendation** | **`yes`** — absolutely keep this on. Memory accounting tells you which services are consuming how much RAM. Critical for detecting memory-hungry malware or resource exhaustion |

### DefaultTasksAccounting=

| | |
|---|---|
| **What it does** | Enables task (process/thread) counting per-unit |
| **Default** | `yes` |
| **Added** | systemd 211 |
| **Recommendation** | **`yes`** — tracking task counts detects fork bombs and process spawning by compromised services |

### DefaultIOAccounting=

| | |
|---|---|
| **What it does** | Enables I/O usage tracking per-unit (read/write bytes) |
| **Default** | `no` |
| **Added** | systemd 211 |
| **Recommendation** | **`yes`** — turn this ON. I/O accounting reveals which services are reading/writing to disk. Rootkits doing disk I/O (modifying files, exfiltrating data) will show up. Minor performance overhead on modern hardware. Your NVMe can handle the accounting |

### DefaultIPAccounting=

| | |
|---|---|
| **What it does** | Enables IP traffic tracking per-unit (bytes sent/received) |
| **Default** | `no` |
| **Added** | systemd 211 |
| **Recommendation** | **`yes`** — turn this ON. IP accounting tracks network bytes per service. Any service phoning home, exfiltrating data, or opening unexpected connections will show traffic. Essential for a system with known compromise |

---

## 8. Resource Management — Tasks and Limits

### DefaultTasksMax=

| | |
|---|---|
| **What it does** | Maximum number of tasks (processes + threads) any single unit can create |
| **Default** | 15% of minimum of `kernel.pid_max`, `kernel.threads-max`, and root cgroup `pids.max` |
| **Added** | systemd 228 |
| **Typical default** | ~4915 (when `pid_max` = 32768) |

#### For Your System (16GB RAM, 16 threads)

Your `kernel.pid_max` is likely 32768 (default for ≤32 cores), so DefaultTasksMax ≈ 4915.

**Recommendation:** Keep default. This prevents any single service from fork-bombing the system. If you need a specific service to run more, override in that unit's config, not globally.

### Default Resource Limits (RLIMIT)

These set process resource limits inherited by all units. Each has a soft:hard format.

| Setting | Limit Type | Default | What It Controls |
|---------|-----------|---------|-----------------|
| `DefaultLimitCPU=` | `RLIMIT_CPU` | unset (unlimited) | Max CPU time in seconds per process |
| `DefaultLimitFSIZE=` | `RLIMIT_FSIZE` | unset (unlimited) | Max file size a process can create |
| `DefaultLimitDATA=` | `RLIMIT_DATA` | unset (unlimited) | Max data segment size |
| `DefaultLimitSTACK=` | `RLIMIT_STACK` | unset (kernel default, 8MB) | Max stack size |
| `DefaultLimitCORE=` | `RLIMIT_CORE` | unset (but PID 1 sets `infinity` internally) | Max core dump file size |
| `DefaultLimitRSS=` | `RLIMIT_RSS` | unset (unlimited) | Max resident set size (not enforced on modern Linux) |
| `DefaultLimitNOFILE=` | `RLIMIT_NOFILE` | **1024:524288** | Max open file descriptors (soft:hard) |
| `DefaultLimitAS=` | `RLIMIT_AS` | unset (unlimited) | Max virtual memory address space |
| `DefaultLimitNPROC=` | `RLIMIT_NPROC` | unset (kernel default) | Max number of processes per user |
| `DefaultLimitMEMLOCK=` | `RLIMIT_MEMLOCK` | **8M** | Max bytes lockable in memory |
| `DefaultLimitLOCKS=` | `RLIMIT_LOCKS` | unset (unlimited) | Max file locks |
| `DefaultLimitSIGPENDING=` | `RLIMIT_SIGPENDING` | unset (kernel default) | Max pending signals |
| `DefaultLimitMSGQUEUE=` | `RLIMIT_MSGQUEUE` | unset (kernel default) | Max bytes in POSIX message queues |
| `DefaultLimitNICE=` | `RLIMIT_NICE` | unset (0) | Max nice priority ceiling |
| `DefaultLimitRTPRIO=` | `RLIMIT_RTPRIO` | unset (0) | Max real-time scheduling priority |
| `DefaultLimitRTTIME=` | `RLIMIT_RTTIME` | unset (unlimited) | Max real-time CPU time without syscall |

#### Hardening Recommendations for i7-10700 / 16GB

| Setting | Hardened Value | Reason |
|---------|---------------|--------|
| `DefaultLimitNOFILE=` | `1024:524288` | Keep default — sane soft limit, high hard limit for apps that need it |
| `DefaultLimitCORE=` | `0:infinity` | Soft=0 (no core dumps by default), hard=infinity (services that need them can opt in). Prevents accidental core dumps leaking memory contents. **For investigation mode: leave as default (infinity) so crashes produce evidence** |
| `DefaultLimitNPROC=` | `4096` | Limit processes per user — stops fork bombs from unprivileged users |
| `DefaultLimitMEMLOCK=` | `8M` | Keep default. Only increase if running encryption/security tools that lock memory (e.g., gpg-agent) |
| `DefaultLimitFSIZE=` | `2G` | Prevent any single process from creating files larger than 2GB by default. Stops log flooding and disk fill attacks |
| `DefaultLimitRTTIME=` | `1000000` | 1 second of real-time CPU without syscall. Prevents RT processes from locking the CPU |

---

## 9. Resource Management — OOM

### DefaultOOMPolicy=

| | |
|---|---|
| **What it does** | Default policy when a process is OOM-killed |
| **Values** | `continue`, `stop`, `kill` |
| **Default** | `continue` |
| **Added** | systemd 243 |
| **`continue`** | Service continues running even if one of its processes was OOM-killed |
| **`stop`** | Service is cleanly stopped after OOM kill |
| **`kill`** | Service is immediately killed (SIGKILL) after OOM kill |
| **Note** | Does NOT apply to services with `Delegate=yes` |
| **Recommendation** | `stop` — if a service gets OOM-killed, cleanly stop it rather than leaving it in a degraded state. On your system with 16GB: OOM events indicate something consuming unexpected memory — you want the service stopped so you can investigate |

### DefaultOOMScoreAdjust=

| | |
|---|---|
| **What it does** | Default OOM score adjustment for all service processes |
| **Values** | Integer -1000 to 1000 |
| **Default** | unset (inherit from PID 1) |
| **Added** | systemd 250 |
| **How it works** | Higher values = more likely to be killed by OOM killer. -1000 = never kill. 1000 = kill first |
| **Recommendation** | Leave unset. Adjust per-service for critical services (set lower to protect them from OOM) |

---

## 10. Resource Management — Memory Pressure

### DefaultMemoryPressureWatch=

| | |
|---|---|
| **What it does** | Whether units monitor memory pressure via PSI (Pressure Stall Information) |
| **Values** | `auto`, `yes`, `no`, `skip` |
| **Default** | `auto` |
| **Added** | systemd 254 |
| **`auto`** | Enable for cgroup-delegated services, based on memory.pressure file availability |
| **Recommendation** | `auto` — let systemd decide based on cgroup configuration. Modern kernels (you have 6.14+) support PSI |

### DefaultMemoryPressureThresholdSec=

| | |
|---|---|
| **What it does** | How long memory pressure must persist before triggering action |
| **Values** | Time span |
| **Default** | `200ms` |
| **Added** | systemd 254 |
| **Recommendation** | `200ms` is fine. Lower = more sensitive (more false triggers on brief spikes), higher = may miss real pressure events |

---

## 11. Hardware Watchdog

This section is **directly relevant** to your ASUS B460M-A. The Intel B460 chipset includes the **Intel TCO Watchdog Timer** (iTCO_wdt).

### Does Your ASUS B460M-A Have a Hardware Watchdog?

**Yes.** The Intel B460 chipset includes the TCO (Total Cost of Ownership) watchdog timer. The kernel driver is `iTCO_wdt`. Check with:

```bash
ls /dev/watchdog*
lsmod | grep iTCO
cat /sys/class/watchdog/watchdog0/identity
```

If you see `/dev/watchdog0` and `iTCO_wdt` is loaded, the hardware watchdog is available.

### RuntimeWatchdogSec=

| | |
|---|---|
| **What it does** | Configures the hardware watchdog to auto-reboot if PID 1 stops pinging it |
| **Values** | Time span, `off`, `default` |
| **Default** | `0` (off) |
| **Device** | `/dev/watchdog0` (or `WatchdogDevice=` path) |
| **Added** | systemd 198 |
| **How it works** | systemd pings the watchdog at half the configured interval. If systemd (PID 1) hangs, becomes unresponsive, or is killed — the watchdog triggers a hardware reboot |
| **Recommendation** | **`30`** (30 seconds) — if PID 1 hangs for 30 seconds, the hardware forces a reboot. This is your **deadman switch** against a frozen system. The rootkit can't prevent a hardware-level reboot |

### RebootWatchdogSec=

| | |
|---|---|
| **What it does** | Watchdog during the shutdown/reboot phase (after PID 1 is replaced by systemd-shutdown) |
| **Values** | Time span |
| **Default** | `10min` |
| **Added** | systemd 198 |
| **Recommendation** | `10min` — if reboot hangs for 10 minutes, hardware forces it. Keep default |

### KExecWatchdogSec=

| | |
|---|---|
| **What it does** | Watchdog during kexec (kernel-to-kernel reboot without BIOS POST) |
| **Values** | Time span |
| **Default** | `off` |
| **Added** | systemd 198 |
| **⚠️ Warning** | Only enable if RuntimeWatchdogSec is also enabled. Some hardware doesn't reset the watchdog on kexec — the system could reboot unexpectedly |
| **Recommendation** | `off` unless you're using kexec regularly. With your rootkit situation, you probably want full cold reboots through BIOS POST anyway — kexec skips firmware checks |

### RuntimeWatchdogPreSec=

| | |
|---|---|
| **What it does** | Pre-timeout notification before the watchdog fires |
| **Values** | Time span (must be less than RuntimeWatchdogSec) |
| **Default** | `0` (off) |
| **Added** | systemd 251 |
| **How it works** | Triggers a pre-timeout event X seconds before the watchdog would reboot. The action is determined by `RuntimeWatchdogPreGovernor=` |
| **Example** | With `RuntimeWatchdogSec=30` and `RuntimeWatchdogPreSec=10`, the pre-timeout fires at 20 seconds (10 seconds before reboot) |
| **Recommendation** | `10` — gives you a 10-second warning before hardware reboot. Combined with `panic` governor, this creates a kernel panic (and core dump) before reboot, giving you forensic data |

### RuntimeWatchdogPreGovernor=

| | |
|---|---|
| **What it does** | What action to take when the pre-timeout fires |
| **Values** | Depends on hardware/driver. Check `/sys/class/watchdog/watchdogX/pretimeout_available_governors` |
| **Common values** | `noop` (just log), `panic` (kernel panic) |
| **Default** | Kernel-configured default (usually `noop`) |
| **Added** | systemd 251 |
| **Recommendation** | `panic` — if the watchdog is about to fire, trigger a kernel panic first. This gives you a crash dump and dmesg output before the hardware reboot. **Critical forensic data** |

### WatchdogDevice=

| | |
|---|---|
| **What it does** | Which watchdog device to use |
| **Values** | Device path |
| **Default** | `/dev/watchdog0` |
| **Added** | systemd 236 |
| **Recommendation** | Default. Your B460 should expose iTCO at `/dev/watchdog0` |

### Complete Watchdog Setup for ASUS B460M-A

```ini
[Manager]
RuntimeWatchdogSec=30
RuntimeWatchdogPreSec=10
RuntimeWatchdogPreGovernor=panic
RebootWatchdogSec=10min
KExecWatchdogSec=off
WatchdogDevice=/dev/watchdog0
```

This means:
- PID 1 pings watchdog every 15 seconds (half of 30)
- If PID 1 stops pinging for 20 seconds → kernel panic (forensic evidence)
- If PID 1 stops pinging for 30 seconds → hardware reboot (guaranteed recovery)
- If reboot hangs for 10 minutes → hardware forces it

---

## 12. Security — Capabilities

### CapabilityBoundingSet=

| | |
|---|---|
| **What it does** | Controls the **maximum set of capabilities** that PID 1 and ALL children can ever have |
| **Values** | Space-separated list of capabilities. Prefix `~` to invert (drop listed, keep rest) |
| **Default** | All capabilities allowed |
| **Added** | systemd 198 |
| **Critical** | Capabilities dropped here **cannot be regained** by any process, even with setuid or unit-level overrides |

#### All Linux Capabilities (as of kernel 6.x)

| Capability | What It Allows | Drop It? |
|-----------|----------------|----------|
| `CAP_AUDIT_CONTROL` | Enable/disable kernel auditing, set audit rules | **KEEP** — you need auditing |
| `CAP_AUDIT_READ` | Read audit log via multicast netlink | **KEEP** — forensics |
| `CAP_AUDIT_WRITE` | Write records to kernel audit log | **KEEP** — logging |
| `CAP_BLOCK_SUSPEND` | Prevent system suspend | Keep |
| `CAP_BPF` | Use bpf() syscall, access BPF programs | **DANGEROUS** — BPF can be used for rootkits. **Consider dropping** if not needed |
| `CAP_CHECKPOINT_RESTORE` | Checkpoint/restore (CRIU) | **DROP** — rarely needed |
| `CAP_CHOWN` | Change file ownership | Keep — needed by services |
| `CAP_DAC_OVERRIDE` | Bypass file read/write/execute permission checks | **DANGEROUS** but needed by root services |
| `CAP_DAC_READ_SEARCH` | Bypass file read and directory search permissions | **DANGEROUS** but needed by some services |
| `CAP_FOWNER` | Bypass permission checks on operations that require file owner match | Keep |
| `CAP_FSETID` | Don't clear setuid/setgid bits on file modification | Keep |
| `CAP_IPC_LOCK` | Lock memory (mlock, mlockall) | Keep — needed by crypto tools |
| `CAP_IPC_OWNER` | Bypass IPC ownership checks | **DROP** if not needed |
| `CAP_KILL` | Send signals to any process | Keep — needed by PID 1 |
| `CAP_LEASE` | Establish file leases | Keep |
| `CAP_LINUX_IMMUTABLE` | Set/clear immutable file flag | **KEEP** — useful for protection |
| `CAP_MAC_ADMIN` | Manage MAC (SMACK/SELinux/AppArmor) | Keep if using MAC |
| `CAP_MAC_OVERRIDE` | Override MAC policy | **DROP** unless absolutely needed |
| `CAP_MKNOD` | Create device special files | Keep — needed by udev |
| `CAP_NET_ADMIN` | Network admin operations | Keep |
| `CAP_NET_BIND_SERVICE` | Bind to ports below 1024 | Keep |
| `CAP_NET_BROADCAST` | Socket broadcast/multicast | Keep |
| `CAP_NET_RAW` | Use raw sockets | **CONSIDER DROPPING** — raw sockets enable packet sniffing. Keep only if you need ping/tcpdump |
| `CAP_PERFMON` | Performance monitoring | **DROP** unless profiling |
| `CAP_SETFCAP` | Set file capabilities | Keep |
| `CAP_SETGID` | Set GID | Keep |
| `CAP_SETPCAP` | Transfer/manage capabilities | Keep |
| `CAP_SETUID` | Set UID | Keep |
| `CAP_SYS_ADMIN` | **GOD MODE** — mount, pivot_root, namespace, BPF, ptrace, and 50+ other things | **DANGEROUS** but **required** for system boot. Cannot be dropped from PID 1 |
| `CAP_SYS_BOOT` | Reboot/kexec | Keep |
| `CAP_SYS_CHROOT` | Use chroot | Keep |
| `CAP_SYS_MODULE` | Load/unload kernel modules | **CRITICAL** — module loading is how rootkits inject code. **Consider dropping after boot** via unit-level restrictions |
| `CAP_SYS_NICE` | Set process priority, CPU affinity | Keep |
| `CAP_SYS_PACCT` | Process accounting | Keep |
| `CAP_SYS_PTRACE` | Trace/debug other processes | **DANGEROUS** — ptrace is used for process injection. Drop where possible |
| `CAP_SYS_RAWIO` | Raw I/O port access, /dev/mem | **EXTREMELY DANGEROUS** — direct hardware/memory access. **DROP** if not needed |
| `CAP_SYS_RESOURCE` | Override resource limits | Keep |
| `CAP_SYS_TIME` | Set system clock | Keep |
| `CAP_SYS_TTY_CONFIG` | Configure TTY devices | Keep |
| `CAP_SYSLOG` | Privileged syslog operations | Keep |
| `CAP_WAKE_ALARM` | Set wake alarms | Keep |

#### Recommended Capability Drop for ASUS B460M-A

```ini
CapabilityBoundingSet=~CAP_CHECKPOINT_RESTORE CAP_PERFMON CAP_MAC_OVERRIDE
```

This is a **conservative** drop. Only removes capabilities that desktop/investigation systems don't need. More aggressive drops risk breaking services. Per-unit capability restrictions (in individual service files) are a better approach for fine-grained control.

**⚠️ WARNING:** Do NOT drop `CAP_SYS_ADMIN`, `CAP_SYS_MODULE`, `CAP_NET_ADMIN`, `CAP_BPF` at the system level without extensive testing — many services depend on them. Instead, drop them per-unit for services that don't need them.

---

## 13. Security — Privilege and System Protection

### NoNewPrivileges=

| | |
|---|---|
| **What it does** | Prevents PID 1 and ALL children from gaining new privileges via execve (no setuid, no setgid, no file capabilities) |
| **Values** | `yes`, `no` |
| **Default** | `no` |
| **Added** | systemd 239 |
| **⚠️ SYSTEM IMPACT** | Setting `yes` globally **breaks**: sudo, su, passwd, pkexec, mount (setuid), screen/tmux, and any program relying on setuid/setgid bits |
| **Recommendation** | **`no`** at system level. This is too destructive globally. Use `NoNewPrivileges=yes` in individual unit files for services that don't need privilege escalation |

### ProtectSystem=

| | |
|---|---|
| **What it does** | Remounts /usr/ read-only at the system manager level |
| **Values** | `yes`/`no`/`auto` |
| **Default** | `auto` (yes in initrd, no otherwise) |
| **Added** | systemd 256 |
| **Note** | This is a **limited** version of the per-unit `ProtectSystem=`. The `full` and `strict` modes are NOT supported at manager level |
| **Recommendation** | `yes` — make /usr/ read-only from PID 1. This prevents modification of system binaries. Your rootkit reports show modified/deleted libraries in /usr/lib/ — this would have blocked that vector. **However:** ensure package updates still work (they'd need to be done in rescue/maintenance mode) |

---

## 14. Security — System Call Architecture Filtering

### SystemCallArchitectures=

| | |
|---|---|
| **What it does** | Restricts which CPU architectures can make system calls **system-wide** |
| **Values** | `native`, `x86`, `x86-64`, `x32`, `arm`, or empty (no filtering) |
| **Default** | Empty (all architectures allowed) |
| **Added** | systemd 209 |
| **What happens on violation** | Process receives `SIGSYS` (immediate termination) |

#### Your System: x86-64

| Setting | Effect |
|---------|--------|
| *(empty)* | Any architecture's syscalls allowed — 32-bit x86 programs work |
| `native` | **Only x86-64 syscalls allowed** — 32-bit programs killed with SIGSYS |
| `x86-64` | Same as native on your system |
| `x86 x86-64` | Both 32-bit and 64-bit allowed (but nothing else like ARM) |

**Recommendation:** **`native`** — restrict to x86-64 only. This is a **powerful security measure**:

1. Blocks 32-bit exploit payloads — many exploits use 32-bit syscalls to bypass ASLR/security features on 64-bit systems
2. Blocks cross-architecture shellcode
3. Blocks execution of 32-bit rootkit components
4. Cost: 32-bit applications (wine, some legacy tools) won't run. Steam 32-bit games won't work.

For your investigation system: **`native`** unless you specifically need 32-bit software.

---

## 15. Security — SMACK and SUID/SGID

### DefaultSmackProcessLabel=

| | |
|---|---|
| **What it does** | Default SMACK security label for all processes |
| **Values** | SMACK64 label string, or `/` (only explicit labels apply) |
| **Default** | unset |
| **Added** | systemd 252 |
| **Relevance** | SMACK is a Mandatory Access Control (MAC) framework. Ubuntu/Mint use AppArmor instead. **Not relevant for your system** unless you switch to SMACK |
| **Recommendation** | Leave unset |

### DefaultRestrictSUIDSGID=

| | |
|---|---|
| **What it does** | Default for whether units can create SUID/SGID files |
| **Values** | `yes` (restrict), `no` (allow) |
| **Default** | unset (no restriction) |
| **Added** | systemd 258 |
| **Recommendation** | **`yes`** — restrict SUID/SGID file creation by default. Services that legitimately need to create setuid files are rare. This prevents a compromised service from dropping setuid binaries as persistence mechanism |

---

## 16. Timeouts and Rate Limits

### Service Timeouts

| Setting | What It Controls | Default (System) | Default (User) |
|---------|-----------------|-------------------|-----------------|
| `DefaultTimeoutStartSec=` | How long a service has to finish starting | 90s | 90s |
| `DefaultTimeoutStopSec=` | How long a service has to finish stopping | 90s | 90s |
| `DefaultTimeoutAbortSec=` | How long to wait for service to abort | unset (falls back to TimeoutStopSec) | unset |
| `DefaultRestartSec=` | Delay between service auto-restarts | 100ms | 100ms |
| `DefaultDeviceTimeoutSec=` | How long to wait for device to appear | 90s | 90s |

#### Recommendations

| Setting | Hardened Value | Reason |
|---------|---------------|--------|
| `DefaultTimeoutStartSec=` | `90s` | Keep default — 90s is generous enough for slow services |
| `DefaultTimeoutStopSec=` | `30s` | **Reduce** — a service that takes >30s to stop is probably hung. Kill it |
| `DefaultTimeoutAbortSec=` | `10s` | **Set** — if a service is aborting, give it 10s then force-kill |
| `DefaultRestartSec=` | `5s` | **Increase** from 100ms — prevents rapid restart loops that consume resources. 5 seconds between restarts is more sane |
| `DefaultDeviceTimeoutSec=` | `90s` | Keep — NVMe and USB devices may need time |

### Rate Limits

| Setting | What It Controls | Default |
|---------|-----------------|---------|
| `DefaultStartLimitIntervalSec=` | Time window for start rate limiting | 10s |
| `DefaultStartLimitBurst=` | Max starts allowed in the window | 5 |
| `ReloadLimitIntervalSec=` | Time window for daemon-reload rate limiting | unset (unlimited) |
| `ReloadLimitBurst=` | Max reloads allowed in the window | unset (unlimited) |

#### Recommendations

| Setting | Hardened Value | Reason |
|---------|---------------|--------|
| `DefaultStartLimitIntervalSec=` | `10s` | Keep default |
| `DefaultStartLimitBurst=` | `5` | Keep — if a service fails 5 times in 10 seconds, it's broken |
| `ReloadLimitIntervalSec=` | `2s` | **Set** — prevent daemon-reload spam |
| `ReloadLimitBurst=` | `5` | **Set** — max 5 reloads per 2 seconds |

---

## 17. Environment Variables

### DefaultEnvironment=

| | |
|---|---|
| **What it does** | Sets environment variables inherited by ALL service processes |
| **Values** | Space-separated `VAR=value` pairs |
| **Default** | Empty |
| **Added** | systemd 205 |
| **Supports** | %-specifiers (see Section 18) |

#### Security-Relevant Environment Variables

```ini
DefaultEnvironment="LANG=C.UTF-8" "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
```

**Recommendation:** Explicitly set `PATH` to prevent path injection attacks where a malicious binary in an unexpected directory gets executed. Don't include `/home/*/bin` or writable paths.

### ManagerEnvironment=

| | |
|---|---|
| **What it does** | Sets environment variables for the PID 1 manager process itself |
| **Values** | Same format as DefaultEnvironment |
| **Default** | Empty |
| **Added** | systemd 248 |
| **Persists** | Through reload and reexec |
| **Note** | User manager: also inherited by spawned processes |

#### Useful Manager Environment Variables

| Variable | Effect |
|----------|--------|
| `SYSTEMD_LOG_LEVEL=debug` | Force debug logging for PID 1 |
| `SYSTEMD_LOG_TARGET=console` | Send manager logs to console |
| `SYSTEMD_LOG_COLOR=false` | Disable color (for machine parsing) |
| `SYSTEMD_EMOJI=0` | Disable emoji in output |

**Recommendation:** Leave empty for production. Set `SYSTEMD_LOG_LEVEL=debug` temporarily when investigating boot issues.

---

## 18. Specifiers Reference

These work in `DefaultEnvironment=` and `ManagerEnvironment=` values.

| Specifier | Meaning | Example Output |
|-----------|---------|----------------|
| `%a` | CPU architecture | `x86-64` |
| `%A` | OS image version (IMAGE_VERSION from os-release) | *(varies)* |
| `%b` | Boot ID (unique per boot) | `a8f6d9e3...` |
| `%B` | OS build ID (BUILD_ID from os-release) | *(varies)* |
| `%H` | Full hostname | `smooth-asus` |
| `%l` | Short hostname (before first dot) | `smooth-asus` |
| `%m` | Machine ID | `abc123...` |
| `%M` | OS image identifier (IMAGE_ID from os-release) | *(varies)* |
| `%o` | OS ID (ID from os-release) | `linuxmint` |
| `%v` | Kernel release (uname -r) | `6.14.0-37-generic` |
| `%w` | OS version ID | `22.3` |
| `%W` | OS variant ID | *(varies)* |
| `%T` | Temp directory | `/tmp` |
| `%V` | Persistent temp directory | `/var/tmp` |
| `%h` | User home directory | `/root` (system), `/home/user` (user) |
| `%u` | Username | `root` (system) |
| `%U` | User ID | `0` (system) |
| `%g` | Primary group | `root` (system) |
| `%G` | Primary group ID | `0` (system) |
| `%s` | User shell | `/bin/bash` |
| `%%` | Literal `%` | `%` |

---

## 19. Deprecated Options

| Option | Status | Replacement |
|--------|--------|-------------|
| `DefaultBlockIOAccounting=` | Deprecated (systemd 252) | Switch to unified cgroup hierarchy (already default on modern systems) |
| `DefaultCPUAccounting=` | Deprecated (systemd 258) | CPU accounting is always enabled on unified cgroup hierarchy — setting has no effect |

---

## 20. ASUS B460M-A / i7-10700 — Complete Hardened Configuration

This is the full drop-in configuration file for your system. Create it at:

**`/etc/systemd/system.conf.d/90-hardened.conf`**

```ini
# =============================================================================
# ASUS PRIME B460M-A / i7-10700 / 16GB RAM
# systemd hardened configuration - Report 25
# ClaudeMKII - 2026-04-18
# =============================================================================

[Manager]

# --- LOGGING ---
# Full logging, timestamps on console, colors on
LogLevel=info
LogTarget=journal-or-kmsg
LogColor=yes
LogTime=yes

# --- CRASH BEHAVIOR ---
# Dump core on crash (forensic evidence)
# Switch to VT1 on crash (see the output)
# No crash shell (security risk)
# Freeze on crash (preserve memory state for investigation)
DumpCore=yes
CrashChangeVT=1
CrashShell=no
CrashAction=freeze

# --- BOOT DISPLAY ---
ShowStatus=yes
StatusUnitFormat=combined
DefaultStandardOutput=journal
DefaultStandardError=inherit

# --- CTRL+ALT+DEL ---
# Disable panic reboot via keyboard
CtrlAltDelBurstAction=none

# --- TIMER ACCURACY ---
DefaultTimerAccuracySec=1min

# --- HARDWARE WATCHDOG (Intel iTCO on B460) ---
RuntimeWatchdogSec=30
RuntimeWatchdogPreSec=10
RuntimeWatchdogPreGovernor=panic
RebootWatchdogSec=10min
KExecWatchdogSec=off
WatchdogDevice=/dev/watchdog0

# --- RESOURCE ACCOUNTING (all ON for monitoring) ---
DefaultMemoryAccounting=yes
DefaultTasksAccounting=yes
DefaultIOAccounting=yes
DefaultIPAccounting=yes

# --- OOM BEHAVIOR ---
DefaultOOMPolicy=stop
# Leave DefaultOOMScoreAdjust unset (inherit)

# --- MEMORY PRESSURE ---
DefaultMemoryPressureWatch=auto
DefaultMemoryPressureThresholdSec=200ms

# --- SECURITY: CAPABILITIES ---
# Conservative drop - only remove clearly unneeded capabilities
CapabilityBoundingSet=~CAP_CHECKPOINT_RESTORE CAP_PERFMON CAP_MAC_OVERRIDE

# --- SECURITY: PRIVILEGE ---
# Do NOT enable NoNewPrivileges globally (breaks sudo/su)
# Do enable SUID/SGID restriction for services
NoNewPrivileges=no
DefaultRestrictSUIDSGID=yes

# --- SECURITY: SYSTEM PROTECTION ---
# Make /usr/ read-only at manager level
ProtectSystem=yes

# --- SECURITY: ARCHITECTURE FILTERING ---
# x86-64 only - blocks 32-bit exploit payloads
SystemCallArchitectures=native

# --- TIMEOUTS ---
DefaultTimeoutStartSec=90s
DefaultTimeoutStopSec=30s
DefaultTimeoutAbortSec=10s
DefaultRestartSec=5s
DefaultDeviceTimeoutSec=90s

# --- START RATE LIMITS ---
DefaultStartLimitIntervalSec=10s
DefaultStartLimitBurst=5

# --- RELOAD RATE LIMITS ---
ReloadLimitIntervalSec=2s
ReloadLimitBurst=5

# --- RESOURCE LIMITS ---
DefaultLimitNOFILE=1024:524288
DefaultLimitMEMLOCK=8M
DefaultLimitNPROC=4096
DefaultLimitRTTIME=1000000

# --- ENVIRONMENT ---
# Explicit PATH - no user-writable directories
DefaultEnvironment="PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
```

### How to Deploy

```bash
# Create the directory if it doesn't exist
sudo mkdir -p /etc/systemd/system.conf.d/

# Copy or create the file
sudo nano /etc/systemd/system.conf.d/90-hardened.conf
# (paste the above config)

# Verify syntax
systemd-analyze cat-config systemd/system.conf

# Apply (requires reboot for full effect, but some take effect on reload)
sudo systemctl daemon-reexec

# Verify after reboot
systemd-analyze blame          # check for timeout/start failures
systemctl --failed             # check for failed units
journalctl -b -p err           # check for errors this boot
cat /proc/1/limits             # verify PID 1 resource limits
```

### Verify Watchdog

```bash
# Check if iTCO watchdog is available
ls -la /dev/watchdog*
cat /sys/class/watchdog/watchdog0/identity
cat /sys/class/watchdog/watchdog0/timeout
cat /sys/class/watchdog/watchdog0/pretimeout
cat /sys/class/watchdog/watchdog0/pretimeout_available_governors

# Check if systemd is pinging it
journalctl -b -u systemd-watchdog* 
systemctl show | grep -i watchdog
```

---

## 21. Kernel Command Line Overrides

Many of these settings can be overridden on the kernel command line (in GRUB). This is useful for one-time debugging without changing config files.

| Kernel Parameter | Overrides |
|-----------------|-----------|
| `systemd.log_level=debug` | LogLevel |
| `systemd.log_target=console` | LogTarget |
| `systemd.log_color=0` | LogColor |
| `systemd.log_location=1` | LogLocation |
| `systemd.log_time=1` | LogTime |
| `systemd.dump_core=1` | DumpCore |
| `systemd.crash_vt=1` | CrashChangeVT |
| `systemd.crash_shell=0` | CrashShell |
| `systemd.crash_action=freeze` | CrashAction |
| `systemd.show_status=1` | ShowStatus |
| `systemd.watchdog_device=/dev/watchdog0` | WatchdogDevice |
| `systemd.cpu_affinity=0-7` | CPUAffinity |
| `systemd.default_standard_output=journal` | DefaultStandardOutput |
| `systemd.default_standard_error=inherit` | DefaultStandardError |

### For Your GRUB Boot Line

Add to kernel cmdline for maximum boot debugging:

```
systemd.log_level=debug systemd.log_time=1 systemd.show_status=1 systemd.crash_action=freeze
```

---

## 22. Related Man Pages — What to Read Next

These are the pages that `systemd-system.conf(5)` references. Each one deepens a specific area.

| Priority | Man Page | What It Covers | Why You Need It |
|----------|----------|----------------|-----------------|
| **1** | **systemd.exec(5)** | Per-unit execution settings: capabilities, namespaces, sandboxing, filesystem protections | **MASSIVE** — this is where per-service hardening lives. Every `ProtectSystem=`, `PrivateTmp=`, `NoNewPrivileges=` per-service |
| **2** | **systemd.resource-control(5)** | Per-unit cgroup controls: memory limits, CPU quotas, I/O bandwidth, IP filtering | Resource limits per service — catch runaway processes |
| **3** | **systemd.service(5)** | Service unit configuration: restart policies, OOM settings, timeouts per-service | Service-specific hardening |
| **4** | **systemd(1)** | The PID 1 binary itself: all kernel command line options, boot sequence, manager behavior | The big picture |
| **5** | **systemd.timer(5)** | Timer units: accuracy, persistent timers, wake-up coalescing | Scheduled task hardening |
| **6** | **capabilities(7)** | Full Linux capabilities reference | Understanding what each CAP_ actually allows |
| **7** | **bootup(7)** | Full boot sequence: generators, units, targets, shutdown sequence | Understanding when configs take effect |
| **8** | **systemd.syntax(7)** | Configuration file syntax rules | How to write correct config files |

### Suggested Next Reports

| Report | Topic | Pages to Cover |
|--------|-------|---------------|
| 26 | systemd.exec(5) — Per-Service Sandboxing | Namespaces, ProtectSystem, PrivateTmp, Capabilities per-unit, SystemCallFilter |
| 27 | systemd.resource-control(5) — Cgroup Controls | MemoryMax, CPUQuota, IOReadBandwidthMax, IPAddressDeny |
| 28 | Kernel hardening cmdline flags | sysctl, BPF restrictions, module loading, ACPI, nomodules |
| 29 | Audit framework (auditd + systemd) | Audit rules, syscall auditing, file integrity monitoring |

---

## APPENDIX A: Quick-Reference Settings Table

Every option from `systemd-system.conf(5)` in one table.

| Option | Section | Default | Hardened Value | Notes |
|--------|---------|---------|---------------|-------|
| LogLevel= | Basic | info | info | debug for investigation |
| LogTarget= | Basic | journal-or-kmsg | journal-or-kmsg | Never null |
| LogColor= | Basic | yes | yes | — |
| LogLocation= | Basic | no | no | yes for debugging |
| LogTime= | Basic | no | **yes** | Forensic timestamps |
| DumpCore= | Basic | yes | yes | Evidence |
| CrashChangeVT= | Basic | no | **1** | See crash output |
| CrashShell= | Basic | no | no | Security risk |
| CrashAction= | Basic | freeze | freeze | Preserve state |
| ShowStatus= | Basic | yes | yes | Watch boot |
| DefaultStandardOutput= | Basic | journal | journal | — |
| DefaultStandardError= | Basic | inherit | inherit | — |
| CtrlAltDelBurstAction= | CtrlAltDel | reboot-force | **none** | Disable panic reboot |
| StatusUnitFormat= | Status | name | **combined** | More info |
| DefaultTimerAccuracySec= | Timer | 1min | 1min | — |
| TimerSlackNSec= | Resource | unset | unset | — |
| CPUAffinity= | Resource | empty | empty | Per-unit better |
| NUMAPolicy= | Resource | default | default | Single-socket: irrelevant |
| NUMAMask= | Resource | empty | empty | Single-socket: irrelevant |
| DefaultMemoryAccounting= | Accounting | yes | yes | — |
| DefaultTasksAccounting= | Accounting | yes | yes | — |
| DefaultIOAccounting= | Accounting | no | **yes** | Catch disk I/O |
| DefaultIPAccounting= | Accounting | no | **yes** | Catch network traffic |
| DefaultTasksMax= | Tasks | ~4915 | default | — |
| DefaultLimitCPU= | Limits | unset | unset | — |
| DefaultLimitFSIZE= | Limits | unset | unset | — |
| DefaultLimitDATA= | Limits | unset | unset | — |
| DefaultLimitSTACK= | Limits | unset | unset | — |
| DefaultLimitCORE= | Limits | unset (infinity) | unset | Keep for forensics |
| DefaultLimitRSS= | Limits | unset | unset | — |
| DefaultLimitNOFILE= | Limits | 1024:524288 | 1024:524288 | — |
| DefaultLimitAS= | Limits | unset | unset | — |
| DefaultLimitNPROC= | Limits | unset | **4096** | Fork bomb protection |
| DefaultLimitMEMLOCK= | Limits | 8M | 8M | — |
| DefaultLimitLOCKS= | Limits | unset | unset | — |
| DefaultLimitSIGPENDING= | Limits | unset | unset | — |
| DefaultLimitMSGQUEUE= | Limits | unset | unset | — |
| DefaultLimitNICE= | Limits | unset | unset | — |
| DefaultLimitRTPRIO= | Limits | unset | unset | — |
| DefaultLimitRTTIME= | Limits | unset | **1000000** | RT safety |
| DefaultOOMPolicy= | OOM | continue | **stop** | Clean stop on OOM |
| DefaultOOMScoreAdjust= | OOM | unset | unset | — |
| DefaultMemoryPressureWatch= | Pressure | auto | auto | — |
| DefaultMemoryPressureThresholdSec= | Pressure | 200ms | 200ms | — |
| RuntimeWatchdogSec= | Watchdog | 0 (off) | **30** | Deadman switch |
| RuntimeWatchdogPreSec= | Watchdog | 0 (off) | **10** | Pre-timeout warning |
| RuntimeWatchdogPreGovernor= | Watchdog | noop | **panic** | Crash dump before reboot |
| RebootWatchdogSec= | Watchdog | 10min | 10min | — |
| KExecWatchdogSec= | Watchdog | off | off | No kexec |
| WatchdogDevice= | Watchdog | /dev/watchdog0 | /dev/watchdog0 | — |
| CapabilityBoundingSet= | Security | all | ~CHECKPOINT_RESTORE PERFMON MAC_OVERRIDE | Conservative |
| NoNewPrivileges= | Security | no | no | Breaks sudo if yes |
| ProtectSystem= | Security | auto | **yes** | /usr/ read-only |
| SystemCallArchitectures= | Security | empty | **native** | Block 32-bit |
| DefaultSmackProcessLabel= | Security | unset | unset | Not using SMACK |
| DefaultRestrictSUIDSGID= | Security | unset | **yes** | Block SUID creation |
| DefaultTimeoutStartSec= | Timeouts | 90s | 90s | — |
| DefaultTimeoutStopSec= | Timeouts | 90s | **30s** | Kill hung services faster |
| DefaultTimeoutAbortSec= | Timeouts | unset | **10s** | Quick abort |
| DefaultRestartSec= | Timeouts | 100ms | **5s** | No rapid restart loops |
| DefaultDeviceTimeoutSec= | Timeouts | 90s | 90s | — |
| DefaultStartLimitIntervalSec= | Rate Limits | 10s | 10s | — |
| DefaultStartLimitBurst= | Rate Limits | 5 | 5 | — |
| ReloadLimitIntervalSec= | Rate Limits | unset | **2s** | Prevent reload spam |
| ReloadLimitBurst= | Rate Limits | unset | **5** | — |
| DefaultEnvironment= | Environment | empty | explicit PATH | No user dirs in PATH |
| ManagerEnvironment= | Environment | empty | empty | — |

---

*End of Report 25*

*Next: Report 26 — systemd.exec(5) Per-Service Sandboxing Breakdown*
*Then: Report 27 — systemd.resource-control(5) Cgroup Controls*
*Then: Report 28 — Kernel Hardening Command Line Flags (nomodules, BPF, ACPI, throttle)*
