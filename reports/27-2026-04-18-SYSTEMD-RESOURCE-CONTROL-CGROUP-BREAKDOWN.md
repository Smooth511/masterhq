# Report 27 — systemd.resource-control(5): Cgroup Resource Controls

**Classification:** SYSTEM HARDENING — FULL REFERENCE GUIDE  
**Prepared by:** ClaudeMKII (MK2PK)  
**Report Date:** 2026-04-18  
**Sources:** https://man.archlinux.org/man/systemd.resource-control.5 (systemd 260.1), cgroups(7), kernel docs  
**System:** ASUS PRIME B460M-A, Intel i7-10700 (8C/16T, 2.9GHz base / 4.8GHz boost), 16GB RAM  
**OS:** Linux Mint 22.3 Zena (Ubuntu 24.04 base)  
**Kernels:** 6.14.0-37-generic, 6.17.0-20-generic  
**Builds on:** Reports 25-26 (system-wide defaults + per-service execution environment)  
**Identifier:** ClaudeMKII-Seed-20260317

---

## TABLE OF CONTENTS

1. [What This Man Page Covers](#1-what-this-man-page-covers)
2. [Controller Hierarchy — How It Works](#2-controller-hierarchy--how-it-works)
3. [CPU Control](#3-cpu-control)
4. [Memory Accounting and Control](#4-memory-accounting-and-control)
5. [Process Accounting and Control](#5-process-accounting-and-control)
6. [IO Accounting and Control](#6-io-accounting-and-control)
7. [Network Accounting and Control](#7-network-accounting-and-control)
8. [BPF Programs](#8-bpf-programs)
9. [Device Access](#9-device-access)
10. [Control Group Management](#10-control-group-management)
11. [Memory Pressure Control](#11-memory-pressure-control)
12. [Coredump Control](#12-coredump-control)
13. [Deprecated Options](#13-deprecated-options)
14. [Hardened Slice Template for ASUS B460M-A](#14-hardened-slice-template-for-asus-b460m-a)
15. [Appendix: Quick-Reference Table — All Options](#appendix-quick-reference-table--all-options)

---

## 1. What This Man Page Covers

`systemd.resource-control(5)` defines **cgroup-based resource limits** — CPU, memory, I/O, network, devices, and process counts. It applies to **six** unit types:

| Unit Type | Section |
|-----------|---------|
| `.service` | `[Service]` |
| `.socket` | `[Socket]` |
| `.mount` | `[Mount]` |
| `.swap` | `[Swap]` |
| `.slice` | `[Slice]` |
| `.scope` | `[Scope]` |

This is the **cgroup v2** resource management layer. Combined with Report 26 (`systemd.exec(5)` — sandboxing) this completes the per-service hardening picture.

### Relationship to Other Reports

| Report | Scope | Relationship |
|--------|-------|-------------|
| **25** (`systemd-system.conf`) | System-wide defaults | `DefaultCPUAccounting=`, `DefaultTasksMax=`, etc. set the baseline |
| **26** (`systemd.exec`) | Execution environment | Sandboxing (namespaces, seccomp, capabilities) |
| **27** (THIS) | Resource limits | CPU, memory, I/O, device, process limits via cgroups |

---

## 2. Controller Hierarchy — How It Works

### Automatic Enablement

Controllers are enabled **automatically** when a unit uses the relevant setting:
- `CPUWeight=` → enables the **cpu** controller
- `MemoryMax=` → enables the **memory** controller
- `TasksMax=` → enables the **pids** controller
- `IOWeight=` → enables the **io** controller

Enabling a controller for one unit **automatically enables it for**:
- All parent slices
- All sibling units in those slices

### Explicit Enablement

- `MemoryAccounting=yes` / `TasksAccounting=yes` / `IOAccounting=yes` — enable accounting even without limits
- `Delegate=` — enables controllers for delegation to child cgroups

### Disabling Controllers

- `DisableControllers=` — prevents specified controllers from being enabled for a unit's children

### Cgroup Hierarchy Example

```
                    -.slice
                   /       \
            system.slice   user.slice
              /       \         \
      a.service    b.slice    user@1000.service
      CPUWeight=20   |         Delegate=yes
                  b1.service     /        \
                              app.slice  session.slice
                              CPUWeight=100
```

Resources are distributed between siblings proportionally by weight. `system.slice` and `user.slice` with no explicit config get equal CPU share (default weight 100 each).

---

## 3. CPU Control

### 3.1 CPUWeight= / StartupCPUWeight=

| Property | Value |
|----------|-------|
| Takes | Integer 1–10000, or `idle` |
| Default | Unset (kernel default: 100) |
| cgroup attribute | `cpu.weight` |
| Added | v232 |

**How weighting works:** Available CPU is split between siblings proportionally by weight.

| Service | Weight | Share of CPU (2 services) |
|---------|--------|--------------------------|
| A | 200 | 200/(200+100) = 67% |
| B | 100 (default) | 100/300 = 33% |

**`idle`**: Only gets CPU when nothing else needs it. Maps to `cpu.idle` cgroup attribute.

**`StartupCPUWeight=`** applies during boot/shutdown; `CPUWeight=` applies during normal runtime.

### 3.2 CPUQuota=

| Property | Value |
|----------|-------|
| Takes | Percentage (e.g. `20%`, `200%`) |
| Default | Unset (no quota) |
| cgroup attribute | `cpu.max` |
| Added | v213 |

**Hard limit** — not work-conserving. `CPUQuota=20%` means max 20% of ONE CPU. Use `200%` to allow full use of 2 CPUs.

**For i7-10700 (16 threads):** `CPUQuota=1600%` would be the maximum.

### 3.3 CPUQuotaPeriodSec=

| Property | Value |
|----------|-------|
| Takes | Time duration |
| Default | 100ms |
| Range | 1ms–1000ms |
| cgroup attribute | Second field of `cpu.max` |
| Added | v242 |

Shorter periods = more responsive CPU limiting but higher overhead.

### 3.4 AllowedCPUs= / StartupAllowedCPUs=

| Property | Value |
|----------|-------|
| Takes | CPU index list/ranges (e.g. `0-3 8-11`) |
| cgroup controller | cpuset |
| Effective | Reported as `EffectiveCPUs=` |
| Added | v244 |

**For i7-10700:**
- Physical cores: 0-7
- Hyperthreads: 8-15
- `AllowedCPUs=0-3` → pin to first 4 cores + their hyperthreads

---

## 4. Memory Accounting and Control

### 4.1 MemoryAccounting=

| Property | Value |
|----------|-------|
| Takes | Boolean |
| Default | `DefaultMemoryAccounting=` (Report 25, default: yes) |
| Added | v208 |

Enabling for one unit enables for ALL units in the same slice and all parent slices.

### 4.2 Memory Protection — MemoryMin= / MemoryLow=

| Option | Effect | Strength | cgroup attr | Added |
|--------|--------|----------|-------------|-------|
| `MemoryMin=` | Hard protection — never reclaimed until this threshold | Strong | `memory.min` | v240 |
| `MemoryLow=` | Soft protection — reclaimed only to avoid OOM | Weak | `memory.low` | v240 |
| `StartupMemoryLow=` | Boot/shutdown variant of MemoryLow | Weak | `memory.low` | v240 |

**Takes:** Bytes (K/M/G/T), percentage of installed RAM, or `infinity`.

**Critical:** Protection MUST be set on ALL ancestor slices. Any unallocated protection is shared between all children.

### 4.3 Memory Throttling — MemoryHigh=

| Option | Effect | cgroup attr | Added |
|--------|--------|-------------|-------|
| `MemoryHigh=` | Soft limit — processes heavily slowed but not killed | `memory.high` | v231 |
| `StartupMemoryHigh=` | Boot/shutdown variant | `memory.high` | v231 |

**This is the main memory control mechanism.** Memory usage CAN exceed this, but processes will be aggressively throttled.

### 4.4 Memory Hard Limit — MemoryMax=

| Option | Effect | cgroup attr | Added |
|--------|--------|-------------|-------|
| `MemoryMax=` | Hard limit — OOM killer invoked if exceeded | `memory.max` | v231 |
| `StartupMemoryMax=` | Boot/shutdown variant | `memory.max` | v231 |

**Effective value** reported as `EffectiveMemoryMax=` (most stringent limit across unit + parent slices, capped by physical RAM).

**Hardening recommendation:** Use `MemoryHigh=` as primary control, `MemoryMax=` as safety net.

### 4.5 Swap Control

| Option | Effect | cgroup attr | Added |
|--------|--------|-------------|-------|
| `MemorySwapMax=` | Hard swap limit | `memory.swap.max` | v232 |
| `StartupMemorySwapMax=` | Boot/shutdown variant | `memory.swap.max` | v232 |

### 4.6 Zswap Control

| Option | Effect | cgroup attr | Added |
|--------|--------|-------------|-------|
| `MemoryZSwapMax=` | Limit compressed swap cache | `memory.zswap.max` | v253 |
| `StartupMemoryZSwapMax=` | Boot/shutdown variant | `memory.zswap.max` | v253 |
| `MemoryZSwapWriteback=` | Allow/deny writeback from zswap to disk | `memory.zswap.writeback` | v256 |

**Zswap** compresses swap pages in RAM before writing to disk. Limiting zswap per-service prevents one service from monopolising the compressed cache.

### 4.7 NUMA Node Restrictions

| Option | Effect | Added |
|--------|--------|-------|
| `AllowedMemoryNodes=` | Restrict to specific NUMA nodes | v244 |
| `StartupAllowedMemoryNodes=` | Boot/shutdown variant | v244 |

**i7-10700:** Single NUMA node — these have no effect.

---

## 5. Process Accounting and Control

### 5.1 TasksAccounting=

| Property | Value |
|----------|-------|
| Takes | Boolean |
| Default | `DefaultTasksAccounting=` (Report 25, default: yes) |
| Added | v227 |

Counts ALL tasks (kernel threads + userspace processes, each thread counted individually).

### 5.2 TasksMax=

| Property | Value |
|----------|-------|
| Takes | Absolute number, percentage (of system max), or `infinity` |
| Default | `DefaultTasksMax=` (Report 25, default: 15% of kernel.pid_max) |
| cgroup attribute | `pids.max` |
| Effective | Reported as `EffectiveTasksMax=` |
| Added | v227 |

**Hardening recommendation:** Set per-service task limits to prevent fork bombs.

```ini
# Web server
TasksMax=256

# Database
TasksMax=1024

# Simple daemon
TasksMax=32
```

---

## 6. IO Accounting and Control

### 6.1 IOAccounting=

| Property | Value |
|----------|-------|
| Takes | Boolean |
| Default | `DefaultIOAccounting=` (Report 25, default: no) |
| Added | v230 |

### 6.2 IOWeight= / StartupIOWeight=

| Property | Value |
|----------|-------|
| Takes | Integer 1–10000 |
| Default | Unset (kernel default: 100) |
| cgroup attribute | `io.weight` |
| Added | v230 |

Proportional I/O bandwidth distribution between siblings, same principle as `CPUWeight=`.

### 6.3 IODeviceWeight=

| Property | Value |
|----------|-------|
| Takes | `DEVICE WEIGHT` pair (e.g. `/dev/sda 1000`) |
| Range | 1–10000 |
| cgroup attribute | `io.weight` (per-device) |
| Added | v230 |

**Device discovery limitations:** Works for simple cases (direct partition, dm-crypt). Does NOT work for RAID or LVM.

### 6.4 IOReadBandwidthMax= / IOWriteBandwidthMax=

| Property | Value |
|----------|-------|
| Takes | `DEVICE BYTES_PER_SEC` pair |
| cgroup attribute | `io.max` |
| NOT work-conserving | Service cannot exceed limit even if device is idle |
| Added | v230 |

### 6.5 IOReadIOPSMax= / IOWriteIOPSMax=

| Property | Value |
|----------|-------|
| Takes | `DEVICE IOPS` pair |
| cgroup attribute | `io.max` |
| NOT work-conserving | Same restriction |
| Added | v230 |

### 6.6 IODeviceLatencyTargetSec=

| Property | Value |
|----------|-------|
| Takes | `DEVICE TIME` pair (e.g. `/dev/sda 25ms`) |
| cgroup attribute | `io.latency` |
| Implies | `IOAccounting=yes` |
| Added | v240 |

---

## 7. Network Accounting and Control

### 7.1 IPAccounting=

| Property | Value |
|----------|-------|
| Takes | Boolean |
| Default | `DefaultIPAccounting=` (Report 25, default: no) |
| System only | Yes |
| Added | v235 |

Accounts all IPv4/IPv6 packet traffic. Socket unit accounting and service accounting are kept separate.

### 7.2 IPAddressAllow= / IPAddressDeny=

| Property | Value |
|----------|-------|
| Takes | IP address/prefix list or symbolic names |
| Implementation | eBPF cgroup filtering |
| Added | v235 |

**Evaluation order:**
1. Check `IPAddressAllow=` — if match → **allow**
2. Check `IPAddressDeny=` — if match → **deny**
3. Default → **allow**

**Symbolic names:**

| Name | IPv4 | IPv6 | Meaning |
|------|------|------|---------|
| `any` | 0.0.0.0/0 | ::/0 | All addresses |
| `localhost` | 127.0.0.0/8 | ::1/128 | Loopback |
| `link-local` | 169.254.0.0/16 | fe80::/64 | Link-local |
| `multicast` | 224.0.0.0/4 | ff00::/8 | Multicast |

**Hardening recommendation — allowlist firewall on system.slice:**
```ini
# /etc/systemd/system/system.slice.d/ip-firewall.conf
[Slice]
IPAddressDeny=any
```
Then per-service:
```ini
[Service]
IPAddressAllow=localhost
IPAddressAllow=192.168.1.0/24
```

### 7.3 SocketBindAllow= / SocketBindDeny=

| Property | Value |
|----------|-------|
| Format | `[address-family:][transport-protocol:][port-or-range]` or `any` |
| Max rules | 128 per directive |
| Implementation | `cgroup/bind4` and `cgroup/bind6` BPF hooks |
| Added | v249 |

**Evaluation order:**
1. Check `SocketBindAllow=` — if match → **allow**
2. Check `SocketBindDeny=` — if match → **deny**
3. Default → **allow**

**Examples:**
```ini
# Only allow binding TCP port 443
SocketBindAllow=tcp:443
SocketBindDeny=any

# Allow binding any port 10000+
SocketBindAllow=10000-65535
SocketBindDeny=any

# Block IPv6 binding
SocketBindDeny=ipv6

# Allow UDP ports 10000-65535 on IPv4 only
SocketBindAllow=ipv4:udp:10000-65535
SocketBindDeny=any
```

**Hardening note:** These apply even across network namespace boundaries — `PrivateNetwork=` does NOT bypass these.

### 7.4 RestrictNetworkInterfaces=

| Property | Value |
|----------|-------|
| Takes | Space-separated interface names |
| Prefix `~` | Deny-list |
| Added | v250 |

The loopback (`lo`) is NOT special — must be explicitly listed.

```ini
# Allow only eth0
RestrictNetworkInterfaces=eth0

# Block everything except lo and eth0
RestrictNetworkInterfaces=lo eth0
```

### 7.5 BindNetworkInterface=

| Property | Value |
|----------|-------|
| Takes | Single interface name |
| Effect | Every socket created by the unit is bound to this interface |
| Implementation | `cgroup/sock_create` BPF hook |
| Added | v260 |

Useful for VRF (Virtual Routing and Forwarding) — equivalent to `ip vrf exec`.

### 7.6 NFTSet=

| Property | Value |
|----------|-------|
| Format | `source:family:table:set` (space-separated) |
| Source types | `cgroup`, `user`, `group` |
| Address families | `arp`, `bridge`, `inet`, `ip`, `ip6`, `netdev` |
| System only | Yes |
| Added | v255 |

Automatically adds/removes cgroup IDs, UIDs, or GIDs to nftables sets when units start/stop. Enables dynamic firewall rules that track service lifecycle.

---

## 8. BPF Programs

### 8.1 IPIngressFilterPath= / IPEgressFilterPath=

| Property | Value |
|----------|-------|
| Takes | Absolute path to pinned BPF program in /sys/fs/bpf/ |
| Effect | Attaches custom IP packet filters to cgroup |
| Added | v243 |

### 8.2 BPFProgram=

| Property | Value |
|----------|-------|
| Format | `type:program-path` |
| Types | `egress`, `ingress`, `sock_create`, `sock_ops`, `device`, `bind4`, `bind6`, `connect4`, `connect6`, `post_bind4`, `post_bind6`, `sendmsg4`, `sendmsg6`, `sysctl`, `recvmsg4`, `recvmsg6`, `getsockopt`, `setsockopt` |
| Attach flag | `BPF_F_ALLOW_MULTI` (allows stacking) |
| Added | v249 |

---

## 9. Device Access

### 9.1 DeviceAllow=

| Property | Value |
|----------|-------|
| Takes | Device specifier + access mode (`r`, `w`, `m`) |
| Device formats | Path (`/dev/sda5`), group (`char-pts`), glob (`char-cpu/*`) |
| Implementation | eBPF |
| Added | v208 |

```ini
# Allow read-only access to a block device
DeviceAllow=/dev/sda r

# Allow all ALSA sound devices (read/write)
DeviceAllow=char-alsa rw

# Allow all CPU-related devices
DeviceAllow=char-cpu/* rwm
```

**For device groups not loaded at boot:** Add `Wants=modprobe@loop.service` + `After=modprobe@loop.service`.

### 9.2 DevicePolicy=

| Value | Effect | Added |
|-------|--------|-------|
| `auto` (default) | Allow all devices if no `DeviceAllow=` set | v208 |
| `closed` | Allow only standard pseudo-devices (null, zero, full, random, urandom) | v208 |
| `strict` | Allow ONLY explicitly listed devices | v208 |

**Hardening recommendation: `closed`** for most services, then add specific `DeviceAllow=` entries.

---

## 10. Control Group Management

### 10.1 Slice=

| Property | Value |
|----------|-------|
| Takes | Slice unit name |
| Default | `system.slice` for non-instantiated, template-based subslice for instances |
| Added | v208 |

### 10.2 Delegate=

| Property | Value |
|----------|-------|
| Takes | Boolean or controller list |
| Default | false |
| Effect | Allows processes in the unit to manage their own cgroup subtree |
| Added | v218 |

**Valid controller names:** `cpu`, `cpuset`, `io`, `memory`, `pids`, `bpf-firewall`, `bpf-devices`, `bpf-foreign`, `bpf-socket-bind`, `bpf-restrict-network-interfaces`, `bpf-bind-network-interface`

**When enabled:**
- The unit owns everything below its cgroup
- systemd won't move processes or manipulate child cgroups
- For unprivileged services (`User=`), the cgroup is made accessible to that user

**Warning:** Controller delegation to unprivileged code is only safe on the **unified** (v2) hierarchy.

### 10.3 DelegateSubgroup=

| Property | Value |
|----------|-------|
| Takes | Control group name (not a path) |
| Default | Off |
| Effect | Places main process in named subgroup instead of cgroup root |
| Requires | `Delegate=` |
| Added | v254 |

Important because **no processes should live in inner nodes** of the cgroup tree. The main supervisor process should be in a subgroup.

### 10.4 DisableControllers=

| Property | Value |
|----------|-------|
| Takes | Space-separated controller names |
| Effect | Prevents listed controllers from being enabled for children |
| Added | v240 |

---

## 11. Memory Pressure Control

### 11.1 ManagedOOMSwap= / ManagedOOMMemoryPressure=

| Property | Value |
|----------|-------|
| Takes | `auto` or `kill` |
| Default | `auto` |
| Added | v247 |

When `kill`: systemd-oomd monitors this unit and kills a descendant cgroup when thresholds are exceeded.

### 11.2 ManagedOOMMemoryPressureLimit=

| Property | Value |
|----------|-------|
| Takes | Percentage 0%–100% |
| Default | 0% (use oomd.conf default) |
| Ignored unless | `ManagedOOMMemoryPressure=kill` |
| Added | v247 |

### 11.3 ManagedOOMMemoryPressureDurationSec=

| Property | Value |
|----------|-------|
| Takes | Time value (minimum 1s) |
| Default | Empty (use oomd.conf default) |
| Added | v257 |

### 11.4 ManagedOOMPreference=

| Property | Value |
|----------|-------|
| Takes | `none`, `avoid`, `omit` |
| Default | `none` |
| Added | v248 |

| Value | Effect |
|-------|--------|
| `none` | Normal OOM kill candidate |
| `avoid` | Only killed if no other candidates |
| `omit` | Completely ignored by systemd-oomd |

**Hardening note:** Use `avoid` or `omit` sparingly — can adversely affect oomd kill behaviour.

### 11.5 MemoryPressureWatch=

| Property | Value |
|----------|-------|
| Takes | Boolean, `auto`, `skip` |
| Default | `DefaultMemoryPressureWatch=` (Report 25, default: auto) |
| Effect | Sets `$MEMORY_PRESSURE_WATCH` and `$MEMORY_PRESSURE_WRITE` for the service |
| Added | v254 |

### 11.6 MemoryPressureThresholdSec=

| Property | Value |
|----------|-------|
| Takes | Time value |
| Default | `DefaultMemoryPressureThresholdSec=` (Report 25, default: 200ms) |
| Effect | Maximum allocation latency before pressure event signalled, per 2s window |
| Added | v254 |

---

## 12. Coredump Control

### 12.1 CoredumpReceive=

| Property | Value |
|----------|-------|
| Takes | Boolean |
| Default | false |
| Effect | Enables coredump forwarding from containers in this cgroup |
| Requires | `Delegate=yes` |
| Added | v255 |

---

## 13. Deprecated Options

These are **cgroup v1** legacy options. They have no effect on cgroup v2 (unified hierarchy). Do NOT use them.

| Option | Replacement | Deprecated since |
|--------|-------------|-----------------|
| `CPUShares=` | `CPUWeight=` | v252 |
| `StartupCPUShares=` | `StartupCPUWeight=` | v252 |
| `MemoryLimit=` | `MemoryMax=` | v252 |
| `BlockIOAccounting=` | `IOAccounting=` | v252 |
| `BlockIOWeight=` | `IOWeight=` | v252 |
| `StartupBlockIOWeight=` | `StartupIOWeight=` | v252 |
| `BlockIODeviceWeight=` | `IODeviceWeight=` | v252 |
| `BlockIOReadBandwidth=` | `IOReadBandwidthMax=` | v252 |
| `BlockIOWriteBandwidth=` | `IOWriteBandwidthMax=` | v252 |
| `CPUAccounting=` | (always on in cgroupv2) | v258 |

---

## 14. Hardened Slice Template for ASUS B460M-A

### System Slice — Resource Containment

```ini
# /etc/systemd/system/system.slice.d/90-resource-limits.conf
[Slice]
# Memory protection: reserve 2GB for system services
MemoryMin=2G
MemoryHigh=12G
MemoryMax=14G

# CPU: default weight, no quota (let services set their own)
# CPUWeight=100

# IO: default weight
# IOWeight=100

# Tasks: limit total system service tasks
TasksMax=4096

# Network firewall: deny all, allow per-service
IPAddressDeny=any

# OOM management
ManagedOOMMemoryPressure=kill
ManagedOOMSwap=kill
```

### Per-Service Example — Web Server

```ini
# /etc/systemd/system/nginx.service.d/90-resources.conf
[Service]
# CPU: slightly higher priority
CPUWeight=150
CPUQuota=400%          # Max 4 cores of 16 threads

# Memory
MemoryHigh=2G
MemoryMax=3G
MemorySwapMax=512M

# IO
IOWeight=200
IOReadBandwidthMax=/dev/nvme0n1 500M
IOWriteBandwidthMax=/dev/nvme0n1 200M

# Tasks
TasksMax=512

# Networking
IPAddressAllow=any
SocketBindAllow=tcp:80
SocketBindAllow=tcp:443
SocketBindDeny=any

# Devices
DevicePolicy=closed

# OOM: avoid killing web server
ManagedOOMPreference=avoid
```

### Per-Service Example — Database

```ini
# /etc/systemd/system/postgresql.service.d/90-resources.conf
[Service]
# CPU: high weight for DB workloads
CPUWeight=300

# Memory: generous allocation for buffer pool
MemoryLow=4G
MemoryHigh=8G
MemoryMax=10G
MemorySwapMax=0        # NEVER swap database pages

# IO: highest priority
IOWeight=500
IODeviceLatencyTargetSec=/dev/nvme0n1 10ms

# Tasks
TasksMax=1024

# Network: only local + subnet
IPAddressAllow=localhost
IPAddressAllow=192.168.1.0/24
SocketBindAllow=tcp:5432
SocketBindDeny=any

# Devices
DevicePolicy=strict
DeviceAllow=/dev/null rw
DeviceAllow=/dev/zero r
DeviceAllow=/dev/urandom r

# OOM: never kill database
ManagedOOMPreference=omit
```

### Per-Service Example — Background Worker

```ini
# /etc/systemd/system/worker.service.d/90-resources.conf
[Service]
# CPU: lowest priority, idle when others need CPU
CPUWeight=idle

# Memory: strict limits
MemoryHigh=512M
MemoryMax=1G

# IO: low priority
IOWeight=10

# Tasks
TasksMax=32

# No network needed
IPAddressDeny=any

# OOM: kill this first
ManagedOOMPreference=none
OOMScoreAdjust=500
```

### Verification

```bash
# Check all resource assignments for a service
systemctl show nginx.service | grep -E '(CPU|Memory|IO|Tasks|IP|Socket|Device)'

# Check effective limits (after parent slice constraints)
systemctl show nginx.service -p EffectiveMemoryMax -p EffectiveMemoryHigh -p EffectiveTasksMax -p EffectiveCPUs

# Monitor resource usage in real-time
systemd-cgtop

# Check cgroup hierarchy
systemd-cgls
```

---

## Appendix: Quick-Reference Table — All Options

| # | Option | Category | Default | cgroup attr | Added |
|---|--------|----------|---------|-------------|-------|
| 1 | `CPUWeight=` | CPU | (unset, kernel: 100) | `cpu.weight` | v232 |
| 2 | `StartupCPUWeight=` | CPU | (unset) | `cpu.weight` | v232 |
| 3 | `CPUQuota=` | CPU | (unset, no quota) | `cpu.max` | v213 |
| 4 | `CPUQuotaPeriodSec=` | CPU | 100ms | `cpu.max` | v242 |
| 5 | `AllowedCPUs=` | CPU | (all) | cpuset | v244 |
| 6 | `StartupAllowedCPUs=` | CPU | (all) | cpuset | v244 |
| 7 | `MemoryAccounting=` | Memory | yes (default) | — | v208 |
| 8 | `MemoryMin=` | Memory | (unset) | `memory.min` | v240 |
| 9 | `MemoryLow=` | Memory | (unset) | `memory.low` | v240 |
| 10 | `StartupMemoryLow=` | Memory | (unset) | `memory.low` | v240 |
| 11 | `MemoryHigh=` | Memory | (unset) | `memory.high` | v231 |
| 12 | `StartupMemoryHigh=` | Memory | (unset) | `memory.high` | v231 |
| 13 | `MemoryMax=` | Memory | (unset) | `memory.max` | v231 |
| 14 | `StartupMemoryMax=` | Memory | (unset) | `memory.max` | v231 |
| 15 | `MemorySwapMax=` | Memory | (unset) | `memory.swap.max` | v232 |
| 16 | `StartupMemorySwapMax=` | Memory | (unset) | `memory.swap.max` | v232 |
| 17 | `MemoryZSwapMax=` | Memory | (unset) | `memory.zswap.max` | v253 |
| 18 | `StartupMemoryZSwapMax=` | Memory | (unset) | `memory.zswap.max` | v253 |
| 19 | `MemoryZSwapWriteback=` | Memory | true | `memory.zswap.writeback` | v256 |
| 20 | `AllowedMemoryNodes=` | Memory | (all) | cpuset | v244 |
| 21 | `StartupAllowedMemoryNodes=` | Memory | (all) | cpuset | v244 |
| 22 | `TasksAccounting=` | Process | yes (default) | — | v227 |
| 23 | `TasksMax=` | Process | 15% of pid_max | `pids.max` | v227 |
| 24 | `IOAccounting=` | IO | no (default) | — | v230 |
| 25 | `IOWeight=` | IO | (unset, kernel: 100) | `io.weight` | v230 |
| 26 | `StartupIOWeight=` | IO | (unset) | `io.weight` | v230 |
| 27 | `IODeviceWeight=` | IO | (unset) | `io.weight` | v230 |
| 28 | `IOReadBandwidthMax=` | IO | (unset) | `io.max` | v230 |
| 29 | `IOWriteBandwidthMax=` | IO | (unset) | `io.max` | v230 |
| 30 | `IOReadIOPSMax=` | IO | (unset) | `io.max` | v230 |
| 31 | `IOWriteIOPSMax=` | IO | (unset) | `io.max` | v230 |
| 32 | `IODeviceLatencyTargetSec=` | IO | (unset) | `io.latency` | v240 |
| 33 | `IPAccounting=` | Network | no (default) | — | v235 |
| 34 | `IPAddressAllow=` | Network | (empty) | eBPF | v235 |
| 35 | `IPAddressDeny=` | Network | (empty) | eBPF | v235 |
| 36 | `SocketBindAllow=` | Network | (empty) | BPF bind hooks | v249 |
| 37 | `SocketBindDeny=` | Network | (empty) | BPF bind hooks | v249 |
| 38 | `RestrictNetworkInterfaces=` | Network | (all) | — | v250 |
| 39 | `BindNetworkInterface=` | Network | (unset) | BPF sock_create | v260 |
| 40 | `NFTSet=` | Network | (empty) | nftables | v255 |
| 41 | `IPIngressFilterPath=` | BPF | (empty) | BPF filter | v243 |
| 42 | `IPEgressFilterPath=` | BPF | (empty) | BPF filter | v243 |
| 43 | `BPFProgram=` | BPF | (empty) | BPF attach | v249 |
| 44 | `DeviceAllow=` | Device | (unset) | eBPF | v208 |
| 45 | `DevicePolicy=` | Device | `auto` | eBPF | v208 |
| 46 | `Slice=` | Cgroup | `system.slice` | — | v208 |
| 47 | `Delegate=` | Cgroup | false | — | v218 |
| 48 | `DelegateSubgroup=` | Cgroup | (off) | — | v254 |
| 49 | `DisableControllers=` | Cgroup | (empty) | — | v240 |
| 50 | `ManagedOOMSwap=` | OOM | `auto` | — | v247 |
| 51 | `ManagedOOMMemoryPressure=` | OOM | `auto` | — | v247 |
| 52 | `ManagedOOMMemoryPressureLimit=` | OOM | 0% | — | v247 |
| 53 | `ManagedOOMMemoryPressureDurationSec=` | OOM | (empty) | — | v257 |
| 54 | `ManagedOOMPreference=` | OOM | `none` | xattr | v248 |
| 55 | `MemoryPressureWatch=` | Pressure | `auto` | — | v254 |
| 56 | `MemoryPressureThresholdSec=` | Pressure | 200ms | — | v254 |
| 57 | `CoredumpReceive=` | Coredump | false | — | v255 |

**Total: 57 options documented.**

---

## Related Reports

| Report | Topic | Status |
|--------|-------|--------|
| **25** | systemd-system.conf(5) — System-wide defaults | ✅ Complete |
| **26** | systemd.exec(5) — Per-service execution (162 options) | ✅ Complete |
| **27** | systemd.resource-control(5) — Cgroup controls (THIS REPORT) | ✅ Complete |
| **28** | Kernel command-line hardening flags | 📋 Next |
| **29** | Audit framework (auditd + systemd) | 📋 Planned |

---

*Report 27 of the masterhq investigation series. 57 options documented from systemd.resource-control(5) with per-option hardening recommendations and ready-to-deploy templates for the ASUS PRIME B460M-A / i7-10700 system.*
