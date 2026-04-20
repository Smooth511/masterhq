# Report 27 — systemd.exec(5): Per-Service Execution Environment & Sandboxing

**Classification:** SYSTEM HARDENING — FULL REFERENCE GUIDE  
**Prepared by:** ClaudeMKII (MK2PK)  
**Report Date:** 2026-04-18  
**Sources:** https://man.archlinux.org/man/systemd.exec.5 (systemd 260.1), capabilities(7), seccomp(2), namespaces(7)  
**System:** ASUS PRIME B460M-A, Intel i7-10700 (8C/16T, 2.9GHz base / 4.8GHz boost), 16GB RAM  
**OS:** Linux Mint 22.3 Zena (Ubuntu 24.04 base)  
**Kernels:** 6.14.0-37-generic, 6.17.0-20-generic  
**Builds on:** Report 26 (systemd-system.conf(5) — system-wide defaults)  
**Identifier:** ClaudeMKII-Seed-20260317

---

## TABLE OF CONTENTS

1. [What This Man Page Covers](#1-what-this-man-page-covers)
2. [Paths — Filesystem View](#2-paths--filesystem-view)
3. [User/Group Identity](#3-usergroup-identity)
4. [Capabilities](#4-capabilities)
5. [Security and Mandatory Access Control](#5-security-and-mandatory-access-control)
6. [Process Properties and Resource Limits](#6-process-properties-and-resource-limits)
7. [Scheduling](#7-scheduling)
8. [Sandboxing — Filesystem Isolation](#8-sandboxing--filesystem-isolation)
9. [Sandboxing — Namespace Isolation](#9-sandboxing--namespace-isolation)
10. [Sandboxing — BPF Controls](#10-sandboxing--bpf-controls)
11. [Sandboxing — Behavioural Lockdown](#11-sandboxing--behavioural-lockdown)
12. [System Call Filtering](#12-system-call-filtering)
13. [Environment Variables](#13-environment-variables)
14. [Logging and Standard I/O](#14-logging-and-standard-io)
15. [Credentials](#15-credentials)
16. [System V Compatibility](#16-system-v-compatibility)
17. [Environment Variables Set by the Manager](#17-environment-variables-set-by-the-manager)
18. [Process Exit Codes](#18-process-exit-codes)
19. [Hardened Service Template for ASUS B460M-A](#19-hardened-service-template-for-asus-b460m-a)
20. [Appendix A: Quick-Reference Table — All Options](#appendix-a-quick-reference-table--all-options)
21. [Appendix B: Predefined System Call Sets](#appendix-b-predefined-system-call-sets)
22. [Appendix C: Predefined Filesystem Sets](#appendix-c-predefined-filesystem-sets)

---

## 1. What This Man Page Covers

`systemd.exec(5)` defines the **execution environment** for every process spawned by systemd. It applies to **four** unit types:

| Unit Type | Section |
|-----------|---------|
| `.service` | `[Service]` |
| `.socket` | `[Socket]` |
| `.mount` | `[Mount]` |
| `.swap` | `[Swap]` |

This is the **single most important man page for service hardening**. While Report 26 covered system-wide defaults (`systemd-system.conf`), this report covers **per-service overrides** — the directives you put in individual unit files or drop-ins to sandbox each service independently.

### Key Concepts

- **Namespace isolation**: Linux kernel namespaces (mount, PID, network, user, UTS, IPC, cgroup) create isolated environments
- **Seccomp filtering**: System call filtering via SECCOMP BPF — block dangerous syscalls per-service
- **Capability bounding**: Drop Linux capabilities from processes that don't need them
- **Filesystem restrictions**: Read-only mounts, inaccessible paths, temporary filesystems

### Investigation Context

Given the rootkit documented in Reports 18 and 24 (Ventoy-based boot chain, MOK cert injection, casper live overlay), per-service sandboxing is critical. A properly sandboxed service **cannot**:
- Load kernel modules (`ProtectKernelModules=yes`)
- Write to `/boot` or `/efi` (`ProtectSystem=strict`)
- Access raw devices (`PrivateDevices=yes`)
- Create SUID binaries (`RestrictSUIDSGID=yes`)
- Use non-native ABIs to bypass seccomp (`SystemCallArchitectures=native`)

---

## 2. Paths — Filesystem View

These settings control what the service's processes see when they look at the filesystem.

### 2.1 ExecSearchPath=

| Property | Value |
|----------|-------|
| Takes | Colon-separated list of absolute paths |
| Default | Not set (uses `$PATH`) |
| Effect | Overrides `$PATH` for `Exec*=` lookups unless `$PATH` is explicitly set via `Environment=` |
| Added | v250 |

**Hardening note:** Can restrict where executables are found, preventing PATH injection attacks.

### 2.2 WorkingDirectory=

| Property | Value |
|----------|-------|
| Takes | Absolute path or `~` (user's home) |
| Default | `/` (system), user's home (user instance) |
| Prefix `-` | Missing directory is non-fatal |
| Effect | `chdir()` before exec |

### 2.3 RootDirectory=

| Property | Value |
|----------|-------|
| Takes | Absolute path (relative to host root) |
| Effect | `pivot_root()` or `chroot()` into specified directory |
| System only | Yes |

**Hardening note:** Creates a filesystem jail. Combine with `MountAPIVFS=yes` and `PrivateDevices=yes` for full containment. The process binary and all dependencies must exist inside the root.

### 2.4 RootImage=

| Property | Value |
|----------|-------|
| Takes | Path to block device or loopback file |
| Effect | Mounts a filesystem image as the service's root |
| Auto-deps | Adds `After=systemd-udevd.service` |
| Added | v233 |

Supports MBR/GPT partition tables and the Discoverable Partitions Specification. When `DevicePolicy=` is "closed" or "strict", automatically adds loop device access to `DeviceAllow=`.

### 2.5 RootImageOptions=

| Property | Value |
|----------|-------|
| Takes | Comma-separated mount options, optionally prefixed with partition name |
| Valid partitions | root, usr, home, srv, esp, xbootldr, tmp, var |
| System only | Yes |
| Added | v247 |

### 2.6 RootEphemeral=

| Property | Value |
|----------|-------|
| Takes | Boolean |
| Default | false |
| Effect | Runs service in an ephemeral (disposable) copy of root directory/image |
| Storage | `/var/lib/systemd/ephemeral-trees/` |
| System only | Yes |
| Added | v254 |

**Hardening note:** Excellent for services that should leave no persistent filesystem traces. Ephemeral copy is destroyed when service stops.

### 2.7 RootHash=

| Property | Value |
|----------|-------|
| Takes | Hex root hash or path to `.roothash` file |
| Effect | Enables dm-verity integrity checking on `RootImage=` |
| Fallback | Checks `user.verity.roothash` xattr, then `.roothash` file adjacent to image |
| Added | v246 |

### 2.8 RootHashSignature=

| Property | Value |
|----------|-------|
| Takes | Path to DER-encoded PKCS7 file, or `base64:` prefixed string |
| Effect | dm-verity volume only opens if signature valid and signed by kernel keyring key |
| Fallback | Checks `.roothash.p7s` file adjacent to image |
| Added | v246 |

### 2.9 RootVerity=

| Property | Value |
|----------|-------|
| Takes | Path to dm-verity data file |
| Effect | Provides external integrity data for `RootImage=` |
| Fallback | Checks `.verity` file adjacent to image |
| Added | v246 |

### 2.10 Image Policy Options

| Option | Default Policy | Added |
|--------|---------------|-------|
| `RootImagePolicy=` | `root=verity+signed+encrypted+unprotected+absent:usr=...` (full chain) | v254 |
| `MountImagePolicy=` | Same as RootImagePolicy | v254 |
| `ExtensionImagePolicy=` | `root=verity+signed+encrypted+unprotected+absent:usr=...` | v254 |

### 2.11 RootMStack=

| Property | Value |
|----------|-------|
| Takes | Path to `.mstack/` directory |
| Effect | Sets up overlayfs-based root from mount stack layers |
| Added | v260 |

### 2.12 MountAPIVFS=

| Property | Value |
|----------|-------|
| Takes | Boolean |
| Effect | Mounts `/proc/`, `/sys/`, `/dev/`, `/run/` (tmpfs) in the service's mount namespace |
| Implied by | `ProtectProc=`, `ProcSubset=`, `ProtectKernelTunables=`, `ProtectControlGroups=`, `PrivatePIDs=` |
| Added | v233 |

### 2.13 BindLogSockets=

| Property | Value |
|----------|-------|
| Takes | Boolean |
| Effect | Bind mounts journald sockets into mount namespace for logging |
| Implied by | `LogNamespace=`, `MountAPIVFS=yes`, `PrivateDevices=yes` with `RootDirectory=/RootImage=` |
| Added | v257 |

### 2.14 ProtectProc=

| Property | Value |
|----------|-------|
| Takes | `noaccess`, `invisible`, `ptraceable`, `default` |
| Default | `default` |
| Effect | Controls `hidepid=` on `/proc/` — hides other users' process metadata |
| Implies | `MountAPIVFS=` |
| System only | Yes |
| Added | v247 |

**Hardening recommendation: `invisible`** — Most services have no business seeing other processes.

| Value | Effect |
|-------|--------|
| `default` | No restrictions |
| `noaccess` | Cannot access most other users' `/proc/PID` entries |
| `invisible` | Other users' processes completely hidden from `/proc/` |
| `ptraceable` | Only processes that can be `ptrace()`d are visible |

**Important:** Root user is unaffected. Must combine with `User=` or `DynamicUser=yes` and drop `CAP_SYS_PTRACE`.

### 2.15 ProcSubset=

| Property | Value |
|----------|-------|
| Takes | `all`, `pid` |
| Default | `all` |
| Effect | With `pid`, hides non-process-management files in `/proc/` (kernel APIs) |
| System only | Yes |
| Added | v247 |

### 2.16 BindPaths= / BindReadOnlyPaths=

| Property | Value |
|----------|-------|
| Takes | Whitespace-separated list of `source:destination:option` triples |
| Options | `rbind` (recursive, default) or `norbind` |
| Prefix `-` | Ignore if source doesn't exist |
| Effect | Unit-specific bind mounts, not visible to host |
| Implies | `PrivateMounts=` |
| Added | v233 |

`BindPaths=` = writable; `BindReadOnlyPaths=` = read-only. Critical for `RootDirectory=/RootImage=` setups — source is on host, destination is inside the root.

### 2.17 MountImages=

| Property | Value |
|----------|-------|
| Takes | Whitespace-separated `source:destination[:options]` |
| Effect | Mounts filesystem images at specific points inside the service's namespace |
| Added | v247 |

### 2.18 ExtensionImages=

| Property | Value |
|----------|-------|
| Takes | Whitespace-separated source paths with optional mount options |
| Effect | Sets up read-only overlayfs on `/usr/`, `/opt/` (sysext) and `/etc/` (confext) |
| Added | v248 |

### 2.19 ExtensionDirectories=

| Property | Value |
|----------|-------|
| Takes | Whitespace-separated directory paths |
| Effect | Same as ExtensionImages but from directories instead of images |
| Added | v251 |

---

## 3. User/Group Identity

**System services only** (not per-user instances).

### 3.1 User= / Group=

| Property | Value |
|----------|-------|
| Takes | Username/groupname or numeric UID/GID |
| Default | `root` (system services) |
| Effect | Runs process as specified user/group |

**Hardening note:** NEVER run a network-facing service as root unless absolutely required. Create a dedicated user.

### 3.2 DynamicUser=

| Property | Value |
|----------|-------|
| Takes | Boolean |
| Default | false |
| UID range | 61184–65519 |
| Effect | Allocates ephemeral user/group at start, releases at stop |
| Added | v232 |

**When enabled, AUTOMATICALLY implies:**
- `RemoveIPC=yes`
- `NoNewPrivileges=yes`
- `RestrictSUIDSGID=yes`
- `ProtectSystem=strict`
- `ProtectHome=read-only`
- `PrivateTmp=disconnected` (if not explicitly set to `true`)

**Hardening note:** This is the **single most powerful hardening toggle**. One setting enables 6+ protections. Use for any stateless network service.

### 3.3 SupplementaryGroups=

| Property | Value |
|----------|-------|
| Takes | Space-separated group names or IDs |
| Effect | Extends (never replaces) the user's default group list |

### 3.4 SetLoginEnvironment=

| Property | Value |
|----------|-------|
| Takes | Boolean |
| Default | true if `User=`/`DynamicUser=`/`PAMName=` set, false otherwise |
| Effect | Controls whether `$HOME`, `$LOGNAME`, `$SHELL` are set |
| Added | v255 |

### 3.5 PAMName=

| Property | Value |
|----------|-------|
| Takes | PAM service name |
| Effect | Opens a PAM session under that name |
| Note | Spawns an `(sd-pam)` helper process for session lifetime |

**Warning:** May cause the main process to migrate to a session scope unit, affecting `NotifyAccess=all` behaviour.

---

## 4. Capabilities

### 4.1 CapabilityBoundingSet=

| Property | Value |
|----------|-------|
| Takes | Whitespace-separated capability names (e.g. `CAP_NET_BIND_SERVICE`) |
| Default | Not modified (all caps retained) |
| Prefix `~` | Invert — listed caps are REMOVED |
| Empty string | Reset to empty set (drop ALL caps) |
| `~` alone | Reset to full set |

**How merging works:**
```
CapabilityBoundingSet=CAP_A CAP_B    # Start with A, B
CapabilityBoundingSet=CAP_B CAP_C    # OR → A, B, C
```
```
CapabilityBoundingSet=CAP_A CAP_B    # Start with A, B
CapabilityBoundingSet=~CAP_B CAP_C   # AND-NOT → only A
```

**Hardening recommendation for most services:**
```ini
CapabilityBoundingSet=~CAP_SYS_ADMIN CAP_SYS_PTRACE CAP_SYS_MODULE CAP_SYS_RAWIO CAP_SYS_BOOT CAP_NET_ADMIN CAP_SYS_TIME CAP_MKNOD CAP_SYS_CHROOT
```

Use `systemd-analyze capability` to list all capabilities on your system.

### 4.2 AmbientCapabilities=

| Property | Value |
|----------|-------|
| Takes | Same format as CapabilityBoundingSet |
| Effect | Grants capabilities to non-root processes via the ambient set |
| Auto-adds | `keep-caps` to `SecureBits=` |
| Added | v229 |

Useful when running as non-root but needing specific caps (e.g. `CAP_NET_BIND_SERVICE` for port 80).

---

## 5. Security and Mandatory Access Control

### 5.1 NoNewPrivileges=

| Property | Value |
|----------|-------|
| Takes | Boolean |
| Default | false |
| Effect | Process and ALL children can NEVER gain privileges via execve() (setuid, setgid, filesystem caps) |
| Implied by | `DynamicUser=yes` |
| Added | v187 |

**Hardening note:** This is the **simplest and most effective** privilege escalation prevention. Enable on every service that doesn't need setuid. Also causes all filesystems to be mounted `MS_NOSUID` when in a new mount namespace with SELinux disabled.

### 5.2 SecureBits=

| Property | Value |
|----------|-------|
| Takes | Space-separated: `keep-caps`, `keep-caps-locked`, `no-setuid-fixup`, `no-setuid-fixup-locked`, `noroot`, `noroot-locked` |
| Default | 0 (all off) |

### 5.3 SELinuxContext=

| Property | Value |
|----------|-------|
| Takes | SELinux security context string |
| Prefix `-` | Ignore failures |
| Added | v209 |

### 5.4 AppArmorProfile=

| Property | Value |
|----------|-------|
| Takes | Profile name (must be loaded in kernel) |
| Prefix `-` | Ignore failures |
| System only | Yes |
| Added | v210 |

### 5.5 SmackProcessLabel=

| Property | Value |
|----------|-------|
| Takes | SMACK64 security label |
| Prefix `-` | Ignore failures |
| System only | Yes |
| Added | v218 |

---

## 6. Process Properties and Resource Limits

### 6.1 Resource Limits (LimitXXX=)

All take either a single value (sets both soft and hard) or `soft:hard`. Use `infinity` for no limit.

| Directive | ulimit | Unit | Notes |
|-----------|--------|------|-------|
| `LimitCPU=` | `-t` | Seconds | Rounds up to 1s granularity |
| `LimitFSIZE=` | `-f` | Bytes | |
| `LimitDATA=` | `-d` | Bytes | **Do not use.** Limits address range, not memory. Leave unlimited. |
| `LimitSTACK=` | `-s` | Bytes | |
| `LimitCORE=` | `-c` | Bytes | Set to 0 to disable core dumps, `infinity` to enable |
| `LimitRSS=` | `-m` | Bytes | **Do not use.** Not implemented on Linux. Use `MemoryMax=` instead. |
| `LimitNOFILE=` | `-n` | FD count | Hard limit defaults to 524288. Don't raise soft above 1023 if using `select(2)`. |
| `LimitAS=` | `-v` | Bytes | **Do not use.** Limits address range. Use `MemoryMax=` instead. |
| `LimitNPROC=` | `-u` | Processes | Per-UID, not per-service. Prefer `TasksMax=` instead. |
| `LimitMEMLOCK=` | `-l` | Bytes | |
| `LimitLOCKS=` | `-x` | Lock count | |
| `LimitSIGPENDING=` | `-i` | Signal count | |
| `LimitMSGQUEUE=` | `-q` | Bytes | |
| `LimitNICE=` | `-e` | Nice level | `+`/`-` prefix = nice value (-20..19); no prefix = raw (0..40) |
| `LimitRTPRIO=` | `-r` | RT priority | |
| `LimitRTTIME=` | `-R` | Microseconds | Default unit is microseconds (not seconds) |

**Multiplier suffixes:** K, M, G, T, P, E (base 1024) for byte values. Time units: ms, s, min, h.

**Hardening recommendation:**
```ini
LimitCORE=0          # Disable core dumps (prevent credential leakage)
LimitNOFILE=1024     # Restrict file descriptors for simple services
LimitNPROC=64        # Limit fork bombs (but prefer TasksMax=)
```

**Defaults** come from `DefaultLimitXXX=` in `systemd-system.conf(5)` (see Report 26).

### 6.2 UMask=

| Property | Value |
|----------|-------|
| Takes | Octal access mode |
| Default | 0022 (system), inherited (user) |

**Hardening:** Use `UMask=0077` for services that create sensitive files.

### 6.3 CoredumpFilter=

| Property | Value |
|----------|-------|
| Takes | Space-separated mapping types or `all`/`default` |
| Default | Inherited (kernel default: `private-anonymous shared-anonymous elf-headers private-huge`) |
| Types | `private-anonymous`, `shared-anonymous`, `private-file-backed`, `shared-file-backed`, `elf-headers`, `private-huge`, `shared-huge`, `private-dax`, `shared-dax` |
| Added | v246 |

### 6.4 KeyringMode=

| Property | Value |
|----------|-------|
| Takes | `inherit`, `private`, `shared` |
| Default | `private` (system services), `inherit` (user/non-service) |
| Added | v235 |

**Hardening:** Keep `private` — prevents key material sharing between services running as the same user (especially root).

### 6.5 OOMScoreAdjust=

| Property | Value |
|----------|-------|
| Takes | Integer -1000 to 1000 |
| Default | Inherited from service manager (normally 0) |
| -1000 | Disables OOM killing for this unit |
| 1000 | Makes this unit the OOM killer's first target |

### 6.6 TimerSlackNSec=

| Property | Value |
|----------|-------|
| Takes | Integer nanoseconds (or time units) |
| Effect | Controls wake-up timer accuracy via `prctl(PR_SET_TIMERSLACK)` |

### 6.7 Personality=

| Property | Value |
|----------|-------|
| Takes | Architecture identifier: `x86-64`, `x86`, `arm64`, `arm`, etc. |
| Default | Not set (host personality) |
| Effect | Controls what `uname(2)` reports |
| Added | v209 |

Useful for running 32-bit services on 64-bit host. On x86-64, supports `x86-64` and `x86`.

### 6.8 IgnoreSIGPIPE=

| Property | Value |
|----------|-------|
| Takes | Boolean |
| Default | true |

---

## 7. Scheduling

### 7.1 Nice=

| Property | Value |
|----------|-------|
| Takes | Integer -20 (highest priority) to 19 (lowest) |
| Default | Inherited |

### 7.2 CPUSchedulingPolicy=

| Property | Value |
|----------|-------|
| Takes | `other`, `batch`, `idle`, `fifo`, `rr`, `ext` |
| Default | `other` (kernel default) |

| Policy | Use Case |
|--------|----------|
| `other` | Normal time-sharing |
| `batch` | CPU-intensive background work |
| `idle` | Only when nothing else needs CPU |
| `fifo` | Real-time, first-in first-out |
| `rr` | Real-time, round-robin |

### 7.3 CPUSchedulingPriority=

| Property | Value |
|----------|-------|
| Takes | 1–99 for real-time policies |

### 7.4 CPUSchedulingResetOnFork=

| Property | Value |
|----------|-------|
| Takes | Boolean |
| Default | false |
| Effect | Resets elevated CPU scheduling on fork() — child processes can't inherit RT priority |

### 7.5 CPUAffinity=

| Property | Value |
|----------|-------|
| Takes | CPU index list, ranges (e.g. `0-3 8-11`), or `numa` |
| Effect | Pins processes to specific CPUs via `sched_setaffinity()` |

**For i7-10700 (8C/16T, cores 0-7, threads 0-15):**
- Isolate critical services to specific cores
- Use `CPUAffinity=0-3` to pin to first 4 physical cores

### 7.6 NUMAPolicy= / NUMAMask=

| Property | Value |
|----------|-------|
| NUMAPolicy | `default`, `preferred`, `bind`, `interleave`, `local` |
| NUMAMask | Node list or `all` |
| Added | v243 |

**i7-10700:** Single-socket, single NUMA node — these settings have no effect on your hardware.

### 7.7 IOSchedulingClass=

| Property | Value |
|----------|-------|
| Takes | `realtime`, `best-effort`, `idle` |
| Default | `best-effort` at priority 4 |

### 7.8 IOSchedulingPriority=

| Property | Value |
|----------|-------|
| Takes | 0 (highest) to 7 (lowest) |
| Default | 4 for `best-effort` |

---

## 8. Sandboxing — Filesystem Isolation

### 8.1 ProtectSystem=

| Property | Value |
|----------|-------|
| Takes | Boolean, `full`, `strict` |
| Default | false |
| Implied by | `DynamicUser=yes` |
| Added | v214 |

| Value | Protection |
|-------|-----------|
| `true` | `/usr/`, `/boot`, `/efi` → read-only |
| `full` | Above + `/etc/` → read-only |
| `strict` | **Entire filesystem** read-only except `/dev/`, `/proc/`, `/sys/` |

**Hardening recommendation: `strict`** — Then use `ReadWritePaths=`, `StateDirectory=`, etc. to whitelist what the service actually needs to write.

### 8.2 ProtectHome=

| Property | Value |
|----------|-------|
| Takes | Boolean, `read-only`, `tmpfs` |
| Default | false |
| Implied by | `DynamicUser=yes` |
| Added | v214 |

| Value | Effect on /home, /root, /run/user |
|-------|----------------------------------|
| `true` | Inaccessible and empty |
| `read-only` | Read-only |
| `tmpfs` | Replaced with empty tmpfs (allows BindPaths to make specific dirs visible) |

**Hardening recommendation: `yes`** for any service that doesn't need user home directories.

### 8.3 Managed Directories

These create directories automatically and set proper ownership. **Use these instead of manual directory creation.**

| Option | System path | User path | Env var |
|--------|------------|-----------|---------|
| `RuntimeDirectory=` | `/run/` | `$XDG_RUNTIME_DIR` | `$RUNTIME_DIRECTORY` |
| `StateDirectory=` | `/var/lib/` | `$XDG_STATE_HOME` | `$STATE_DIRECTORY` |
| `CacheDirectory=` | `/var/cache/` | `$XDG_CACHE_HOME` | `$CACHE_DIRECTORY` |
| `LogsDirectory=` | `/var/log/` | `$XDG_STATE_HOME/log/` | `$LOGS_DIRECTORY` |
| `ConfigurationDirectory=` | `/etc/` | `$XDG_CONFIG_HOME` | `$CONFIGURATION_DIRECTORY` |

**Added:** v211 | **Modes:** v234 | **Quotas:** v258 | **Accounting:** v258

- `RuntimeDirectory=` cleaned up on stop (configurable via `RuntimeDirectoryPreserve=`)
- State/Cache/Logs survive stops
- With `DynamicUser=`, paths use `/var/*/private/` with symlinks to prevent UID recycling attacks
- Mode defaults: `0755` for all
- Third parameter `::ro` makes directory read-only for the service (v257+)
- Quota support via `StateDirectoryQuota=`, `CacheDirectoryQuota=`, `LogsDirectoryQuota=` (requires `prjquota` on filesystem)

### 8.4 RuntimeDirectoryPreserve=

| Value | Effect |
|-------|--------|
| `no` (default) | Removed when service stops |
| `restart` | Preserved on restart, removed on stop |
| `yes` | Never removed (but /run/ is tmpfs, so lost on reboot) |

### 8.5 TimeoutCleanSec=

| Property | Value |
|----------|-------|
| Takes | Time value |
| Default | `infinity` |
| Effect | Timeout for `systemctl clean` operations |
| Added | v244 |

### 8.6 ReadWritePaths= / ReadOnlyPaths= / InaccessiblePaths= / ExecPaths= / NoExecPaths=

| Option | Effect |
|--------|--------|
| `ReadWritePaths=` | Paths accessible with normal permissions |
| `ReadOnlyPaths=` | Paths read-only (writable in host, read-only in service) |
| `InaccessiblePaths=` | Paths completely inaccessible |
| `ExecPaths=` | Paths where execution is allowed |
| `NoExecPaths=` | Paths where execution is denied |

**Nesting:** `ReadWritePaths=` inside `ReadOnlyPaths=` works. `ExecPaths=` inside `NoExecPaths=` works.

**Prefix `-`**: Ignore if path doesn't exist. **Prefix `+`**: Relative to `RootDirectory=`.

**Warning:** Mount propagation from host is NOT blocked for existing mounts — writable host mounts appearing under `ReadOnlyPaths=` remain writable. Combine with `CapabilityBoundingSet=~CAP_SYS_ADMIN` or `SystemCallFilter=~@mount`.

**Example allow-list:**
```ini
[Service]
ReadOnlyPaths=/
ReadWritePaths=/var /run
InaccessiblePaths=-/lost+found
NoExecPaths=/
ExecPaths=/usr/sbin/my_daemon /usr/lib /usr/lib64
```

### 8.7 TemporaryFileSystem=

| Property | Value |
|----------|-------|
| Takes | Space-separated mount points with optional `:options` |
| Default options | `nodev,strictatime,mode=0755` |
| Added | v238 |

Creates tmpfs mounts that hide everything underneath. Combine with `BindPaths=` or `BindReadOnlyPaths=` to expose specific items.

```ini
TemporaryFileSystem=/var:ro
BindReadOnlyPaths=/var/lib/systemd
# Process sees empty /var/ except /var/lib/systemd
```

---

## 9. Sandboxing — Namespace Isolation

### 9.1 PrivateTmp=

| Property | Value |
|----------|-------|
| Takes | Boolean or `disconnected` |
| Default | false |
| Effect | Private `/tmp/` and `/var/tmp/` not shared with other processes |
| Added | v209 |

| Value | Behaviour |
|-------|-----------|
| `true` | Private tmp backed by host's `/tmp/` — shareable via `JoinsNamespaceOf=` |
| `disconnected` | Fully independent tmpfs — NOT shareable, completely isolated |

**Hardening recommendation: `yes`** for all services. Use `disconnected` for maximum isolation.

### 9.2 PrivateDevices=

| Property | Value |
|----------|-------|
| Takes | Boolean |
| Default | false |
| Effect | New `/dev/` with only API pseudo-devices (null, zero, random, urandom, tty) — no physical devices |
| Added | v209 |

**When enabled, also:**
- Installs seccomp filter blocking `@raw-io` syscalls
- Removes `CAP_MKNOD` and `CAP_SYS_RAWIO` from bounding set
- Sets `DevicePolicy=closed`
- `/dev/` mounted read-only and noexec

**Hardening recommendation: `yes`** for ALL services except those that directly need hardware access.

### 9.3 PrivateNetwork=

| Property | Value |
|----------|-------|
| Takes | Boolean |
| Default | false |
| Effect | New network namespace with only loopback (`lo`) |
| Implies | `PrivateMounts=` |

**Warning:** Disconnects `AF_NETLINK` (udev events) and abstract `AF_UNIX` sockets.

**Hardening recommendation: `yes`** for services that do no networking (log processors, local computation, etc.).

### 9.4 PrivateUsers=

| Property | Value |
|----------|-------|
| Takes | Boolean, `self`, `identity`, `full`, `managed` |
| Default | false |
| Added | v232 |

| Value | Effect |
|-------|--------|
| `true`/`self` | Minimal mapping: root + unit's user → themselves, everything else → nobody |
| `identity` | Identity mapping for first 65536 UIDs/GIDs |
| `full` | Identity mapping for ALL UIDs/GIDs + allows setgroups() |
| `managed` | Dynamic 65536-UID range allocated, UID 0 inside maps to dynamic host UID |

### 9.5 PrivatePIDs=

| Property | Value |
|----------|-------|
| Takes | Boolean |
| Default | false |
| Effect | New PID namespace — process becomes PID 1 |
| Implies | `MountAPIVFS=yes` |
| Not compatible with | `Type=forking` |
| Added | v257 |

### 9.6 PrivateIPC=

| Property | Value |
|----------|-------|
| Takes | Boolean |
| Default | false |
| Effect | New IPC namespace (SysV IPC + POSIX message queues) |
| Note | Does NOT affect AF_UNIX sockets or POSIX shared memory |
| Added | v248 |

### 9.7 PrivateMounts=

| Property | Value |
|----------|-------|
| Takes | Boolean |
| Default | false |
| Effect | New mount namespace, propagation from service → host turned off |
| Implied by | PrivateTmp, PrivateDevices, ProtectSystem, ProtectHome, ReadOnlyPaths, etc. |
| Added | v239 |

### 9.8 ProtectHostname=

| Property | Value |
|----------|-------|
| Takes | Boolean or `private` |
| Default | false |
| Added | v242 |

| Value | Effect |
|-------|--------|
| `true` | Prevents changing hostname/domainname |
| `private` | New UTS namespace — can change hostname but only within the namespace |

Optional syntax: `yes:myhostname` or `private:service.local`

### 9.9 Network/IPC/User Namespace Path Options

| Option | Effect | Added |
|--------|--------|-------|
| `UserNamespacePath=` | Joins existing user namespace | v259 |
| `NetworkNamespacePath=` | Joins existing network namespace (e.g. `/proc/$PID/ns/net`) | v242 |
| `IPCNamespacePath=` | Joins existing IPC namespace | v248 |

### 9.10 MountFlags=

| Property | Value |
|----------|-------|
| Takes | `shared`, `slave`, `private` |
| Default | `shared` (after implicit `slave` from other namespace settings) |

**Do not use `private`** — causes temporary mounts (removable media) to stay indefinitely busy in service processes.

### 9.11 ProtectKernelTunables=

| Property | Value |
|----------|-------|
| Takes | Boolean |
| Default | false |
| Effect | Makes `/proc/sys/`, `/sys/`, `/proc/sysrq-trigger`, `/proc/acpi`, `/proc/timer_stats`, `/proc/fs`, `/proc/irq` read-only; `/proc/kallsyms` and `/proc/kcore` inaccessible |
| Implies | `MountAPIVFS=` |
| Added | v232 |

**Hardening recommendation: `yes`** — Kernel tunables should be set at boot, not by services.

### 9.12 ProtectKernelModules=

| Property | Value |
|----------|-------|
| Takes | Boolean |
| Default | false |
| Effect | Blocks module loading/unloading, removes `CAP_SYS_MODULE`, makes `/usr/lib/modules` inaccessible |
| Added | v232 |

**Hardening recommendation: `yes`** — The rootkit in Report 24 used kernel modules. Block module loading for every service that doesn't explicitly need it.

### 9.13 ProtectKernelLogs=

| Property | Value |
|----------|-------|
| Takes | Boolean |
| Default | false |
| Effect | Removes `CAP_SYSLOG`, blocks `syslog(2)` syscall, makes `/dev/kmsg` and `/proc/kmsg` inaccessible |
| Added | v244 |

**Hardening recommendation: `yes`** — Services should not read/write the kernel log ring buffer.

### 9.14 ProtectControlGroups=

| Property | Value |
|----------|-------|
| Takes | Boolean, `private`, `strict` |
| Default | false |
| Added | v232 |

| Value | Effect |
|-------|--------|
| `true` | `/sys/fs/cgroup/` read-only |
| `private` | Private writable cgroup namespace |
| `strict` | Private read-only cgroup namespace |

**Hardening recommendation: `true`** or `strict`.

### 9.15 ProtectClock=

| Property | Value |
|----------|-------|
| Takes | Boolean |
| Default | false |
| Effect | Blocks hardware/system clock writes, removes `CAP_SYS_TIME` + `CAP_WAKE_ALARM`, makes `/dev/rtc*` read-only |
| Added | v245 |

**Hardening recommendation: `yes`** — Only NTP services need clock write access.

### 9.16 MemoryKSM=

| Property | Value |
|----------|-------|
| Takes | Boolean |
| Effect | Enables Kernel Samepage Merging for process memory de-duplication |
| Note | Only enable for processes sharing the same security domain |
| Added | v254 |

### 9.17 MemoryTHP=

| Property | Value |
|----------|-------|
| Takes | `inherit`, `disable`, `madvise`, `system` |
| Default | `inherit` |
| Effect | Controls Transparent Hugepages (2MB vs 4KB pages) per-process |
| Added | v260 |

**i7-10700 note:** THP is generally beneficial for your 16GB system, but can cause latency spikes. Use `madvise` for latency-sensitive services.

---

## 10. Sandboxing — BPF Controls

### 10.1 PrivateBPF=

| Property | Value |
|----------|-------|
| Takes | Boolean |
| Default | false |
| Effect | Mounts private BPF filesystem on `/sys/fs/bpf/`, hiding host's loaded programs and maps |
| Added | v258 |

### 10.2 BPF Delegation Options

These control what BPF capabilities are available inside the private BPF namespace. All require `PrivateBPF=yes`.

| Option | Controls | Example Values | Added |
|--------|----------|----------------|-------|
| `BPFDelegateCommands=` | BPF commands (`delegate_cmds`) | `BPFMapCreate`, `BPFProgLoad`, `any` | v258 |
| `BPFDelegateMaps=` | BPF map types (`delegate_maps`) | `BPFMapTypeHash`, `BPFMapTypeArray`, `any` | v258 |
| `BPFDelegatePrograms=` | BPF program types (`delegate_progs`) | `BPFProgTypeSocketFilter`, `BPFProgTypeCgroupSkb`, `any` | v258 |
| `BPFDelegateAttachments=` | BPF attach points (`delegate_attachs`) | `BPFCgroupInetIngress`, `BPFCgroupInetEgress`, `any` | v258 |

**Hardening note:** Most services should NOT have BPF access. Leave these unset unless the service specifically needs eBPF capabilities. The rootkit investigation context (Report 18) highlighted BPF as an attack vector.

---

## 11. Sandboxing — Behavioural Lockdown

### 11.1 RestrictAddressFamilies=

| Property | Value |
|----------|-------|
| Takes | `none`, or space-separated address families (e.g. `AF_UNIX AF_INET AF_INET6`) |
| Prefix `~` | Deny-list |
| Default | No restrictions |
| Added | v211 |

**Hardening recommendation:**
```ini
# For services needing only local + IPv4/IPv6:
RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6

# For services needing NO network:
RestrictAddressFamilies=AF_UNIX

# Block exotic protocols:
RestrictAddressFamilies=~AF_PACKET AF_NETLINK
```

**Limitation:** Only effective on x86-64, not on 32-bit x86. Combine with `SystemCallArchitectures=native`.

### 11.2 RestrictFileSystems=

| Property | Value |
|----------|-------|
| Takes | Space-separated filesystem names or `@sets` |
| Prefix `~` | Deny-list |
| Added | v250 |

See Appendix C for predefined sets. Example:
```ini
RestrictFileSystems=@basic-api @temporary ext4
```

### 11.3 RestrictNamespaces=

| Property | Value |
|----------|-------|
| Takes | Boolean, or space-separated: `cgroup`, `ipc`, `net`, `mnt`, `pid`, `user`, `uts`, `time` |
| Default | false (no restrictions) |
| Prefix `~` | Deny-list |
| Added | v233 |

**Hardening recommendation: `true`** — Prevents the service from creating any new namespaces (blocks `unshare()`, `clone()` namespace flags, `setns()` with zero flags).

### 11.4 DelegateNamespaces=

| Property | Value |
|----------|-------|
| Takes | Boolean, or namespace type list |
| Default | false |
| Effect | Delegates namespace ownership to the unit's user namespace |
| Implies | `PrivateUsers=self` if not already set |
| Added | v258 |

### 11.5 LockPersonality=

| Property | Value |
|----------|-------|
| Takes | Boolean |
| Default | false |
| Effect | Locks `personality(2)` — prevents changing kernel execution domain |
| Added | v235 |

**Hardening recommendation: `yes`** — Odd personality emulations are poorly tested and may be exploitable.

### 11.6 MemoryDenyWriteExecute=

| Property | Value |
|----------|-------|
| Takes | Boolean |
| Default | false |
| Effect | Blocks creating W+X memory mappings (mmap with PROT_WRITE+PROT_EXEC), changing mappings to executable, and executing shared memory |
| Added | v231 |

**Blocks:** `mmap(PROT_WRITE|PROT_EXEC)`, `mprotect(PROT_EXEC)`, `pkey_mprotect(PROT_EXEC)`, `shmat(SHM_EXEC)`

**Incompatible with:** JIT engines, executable stacks, C compiler trampolines.

**Hardening recommendation: `yes`** for all services except those needing JIT (Node.js, Python with C extensions, Java, etc.).

**Bypass warning:** Can be circumvented via `memfd_create()` or writing to non-noexec filesystems. Block with `InaccessiblePaths=/dev/shm` and `SystemCallFilter=~memfd_create`.

### 11.7 RestrictRealtime=

| Property | Value |
|----------|-------|
| Takes | Boolean |
| Default | false |
| Effect | Blocks `SCHED_FIFO`, `SCHED_RR`, `SCHED_DEADLINE` |
| Added | v231 |

**Hardening recommendation: `yes`** — Realtime scheduling can monopolise CPU for DoS.

### 11.8 RestrictSUIDSGID=

| Property | Value |
|----------|-------|
| Takes | Boolean |
| Default | Value of `DefaultRestrictSUIDSGID=` (see Report 26, default: false) |
| Implied by | `DynamicUser=yes` |
| Added | v242 |

**Hardening recommendation: `yes`** — Blocks creation of SUID/SGID files and directories.

### 11.9 RemoveIPC=

| Property | Value |
|----------|-------|
| Takes | Boolean |
| Default | false |
| Implied by | `DynamicUser=yes` |
| Effect | Removes all SysV/POSIX IPC objects owned by service user/group on stop |
| System only | Yes |
| Added | v232 |

---

## 12. System Call Filtering

### 12.1 SystemCallFilter=

| Property | Value |
|----------|-------|
| Takes | Space-separated syscall names or `@groups` |
| Prefix `~` | Deny-list |
| Default action | `SIGSYS` (terminate) — override with `SystemCallErrorNumber=` |
| Per-call override | `~syscall_name:ERRNO` (e.g. `~@clock:EPERM`) |
| Added | v187 |

**Always implicitly allowed:** `execve()`, `exit()`, `exit_group()`, `getrlimit()`, `rt_sigreturn()`, `sigreturn()`, time queries, `nanosleep()`

**Recommended starting point for most services:**
```ini
[Service]
SystemCallFilter=@system-service
SystemCallErrorNumber=EPERM
```

See **Appendix B** for full list of predefined system call groups.

**Important interaction:** Combine filesystem namespacing (`ProtectSystem=`, `PrivateTmp=`, etc.) with `SystemCallFilter=~@mount` to prevent processes from undoing mount namespace restrictions.

### 12.2 SystemCallErrorNumber=

| Property | Value |
|----------|-------|
| Takes | errno number (1-4095), name (e.g. `EPERM`, `EACCES`), or `kill` |
| Default | `kill` (process terminated with SIGSYS) |
| Added | v209 |

**Hardening recommendation: `EPERM`** — Returns "permission denied" instead of killing the process, which is more graceful and allows better logging.

### 12.3 SystemCallArchitectures=

| Property | Value |
|----------|-------|
| Takes | Space-separated architecture IDs or `native` |
| Default | Empty (no filtering) |
| Added | v209 |

**Hardening recommendation: `native`** — This is **critical** on x86-64. It blocks 32-bit (x86/i686) syscalls, preventing circumvention of seccomp filters via the 32-bit ABI. Many seccomp bypasses rely on switching to 32-bit mode.

### 12.4 SystemCallLog=

| Property | Value |
|----------|-------|
| Takes | Space-separated syscall names or groups |
| Prefix `~` | Log everything EXCEPT listed |
| Effect | Logs matching syscalls via seccomp (for auditing/debugging) |
| Added | v247 |

---

## 13. Environment Variables

### 13.1 Environment=

| Property | Value |
|----------|-------|
| Takes | Space-separated `VAR=value` assignments (quote with `"` for spaces) |
| Effect | Sets environment variables for executed processes |

**Security warning:** Environment variables are exposed via D-Bus and propagated across security boundaries. **NEVER put secrets in Environment=.** Use credentials instead (see Section 15).

### 13.2 EnvironmentFile=

| Property | Value |
|----------|-------|
| Takes | Absolute path to file (prefix `-` for optional) |
| Format | One `VAR=value` per line; `#` and `;` for comments |
| Supports | Unquoted, single-quoted, double-quoted values with POSIX shell escaping |

### 13.3 PassEnvironment=

| Property | Value |
|----------|-------|
| Takes | Space-separated variable names |
| Effect | Passes specified variables from service manager to service |
| Note | No effect for user manager (all vars inherited anyway) |
| Added | v228 |

### 13.4 UnsetEnvironment=

| Property | Value |
|----------|-------|
| Takes | Space-separated variable names or `VAR=value` assignments |
| Effect | Final step — removes matching variables from compiled environment |
| Added | v235 |

**Priority order (later wins):**
1. `DefaultEnvironment=` (systemd-system.conf)
2. Manager-defined variables
3. Manager's own environment (via `PassEnvironment=`)
4. `Environment=` in unit file
5. `EnvironmentFile=`
6. PAM modules (if `PAMName=` used)
7. `UnsetEnvironment=` removes from final result

---

## 14. Logging and Standard I/O

### 14.1 StandardInput=

| Value | Effect |
|-------|--------|
| `null` (default) | Connected to `/dev/null` |
| `tty` | Connected to TTY (process becomes controlling) |
| `tty-force` | Force TTY control (removes previous controller) |
| `tty-fail` | Fail if TTY already has controller |
| `data` | Data from `StandardInputText=`/`StandardInputData=` |
| `file:PATH` | Connected to file/FIFO/AF_UNIX socket |
| `socket` | Socket activation (requires `Accept=yes`) |
| `fd:NAME` | Named file descriptor from socket unit |

### 14.2 StandardOutput=

| Value | Effect |
|-------|--------|
| `inherit` (default when stdin is tty/socket/fd) | Duplicates stdin |
| `null` | Connected to `/dev/null` |
| `tty` | Connected to TTY |
| `journal` | Connected to systemd journal |
| `kmsg` | Connected to kernel log buffer + journal |
| `journal+console` | Journal + system console |
| `kmsg+console` | Kernel log + console |
| `file:PATH` | Write to file (created if missing) |
| `append:PATH` | Append to file |
| `truncate:PATH` | Truncate and write |
| `socket` | Socket activation |
| `fd:NAME` | Named file descriptor |

Default: Value of `DefaultStandardOutput=` in systemd-system.conf (default: `journal`).

### 14.3 StandardError=

Same options as `StandardOutput=`. Default: `DefaultStandardError=` (default: `inherit` from stdout).

### 14.4 StandardInputText= / StandardInputData=

| Option | Format |
|--------|--------|
| `StandardInputText=` | Text with C-style escapes and %-specifiers, newline appended |
| `StandardInputData=` | Base64-encoded binary data |

Both operate on the same buffer. Can be mixed. Empty string resets.

### 14.5 Log Level Controls

| Option | Takes | Effect | Added |
|--------|-------|--------|-------|
| `LogLevelMax=` | syslog level (emerg..debug) | Drops messages above this level | v236 |
| `LogExtraFields=` | `FIELD=VALUE` pairs | Adds custom journal fields to all log records | v236 |
| `LogRateLimitIntervalSec=` | Time | Rate limit window | v240 |
| `LogRateLimitBurst=` | Integer | Max messages per window | v240 |
| `LogFilterPatterns=` | Extended regex | Filter log messages by content; prefix `~` to deny | v253 |
| `LogNamespace=` | Namespace name | Runs logging in separate journal namespace | v245 |

### 14.6 Syslog Options

| Option | Takes | Default |
|--------|-------|---------|
| `SyslogIdentifier=` | Process name tag | Process name |
| `SyslogFacility=` | Facility (kern, user, daemon, auth, etc.) | `daemon` |
| `SyslogLevel=` | Level (emerg..debug) | `info` |
| `SyslogLevelPrefix=` | Boolean | `true` (parse `<N>` prefixes in log lines) |

### 14.7 TTY Options

| Option | Takes | Default |
|--------|-------|---------|
| `TTYPath=` | Device path | `/dev/console` |
| `TTYReset=` | Boolean | false |
| `TTYVHangup=` | Boolean | false |
| `TTYColumns=` / `TTYRows=` | Integer | Auto-detect or kernel default (80×24) |
| `TTYVTDisallocate=` | Boolean | false (deallocates VT, clears screen) |

---

## 15. Credentials

Credentials are the **secure** way to pass secrets to services. They are:
- Limited-size binary/text objects
- Available via `$CREDENTIALS_DIRECTORY` (read-only, in unswappable memory if possible)
- Only accessible to the service's UID + root
- Max 1 MB accumulated per unit

### 15.1 LoadCredential=

| Property | Value |
|----------|-------|
| Format | `ID:PATH` |
| Absolute path | Read from file or connect to AF_UNIX stream socket |
| Relative path | Search: service manager received credentials → `/etc/credstore/` → `/run/credstore/` → `/usr/lib/credstore/` |
| Directory path | Loads every file recursively as `ID_FILENAME` |
| Added | v247 |

### 15.2 LoadCredentialEncrypted=

Same as `LoadCredential=` but credential is decrypted and authenticated before passing to process. Encrypted with:
- TPM2 secret key
- `/var/lib/systemd/credential.secret`
- Or both

Also searches `*.encrypted/` directories.

### 15.3 ImportCredential=

| Property | Value |
|----------|-------|
| Format | Credential name or glob (only trailing `*` supported) |
| Effect | Imports matching credentials from manager or credstore |
| Rename | `original:renamed` syntax supported |
| Priority | Lower than LoadCredential/LoadCredentialEncrypted |
| Added | v254 |

### 15.4 SetCredential= / SetCredentialEncrypted=

| Option | Format | Use |
|--------|--------|-----|
| `SetCredential=` | `ID:VALUE` (C-style escapes) | Embed **non-secret** data directly in unit file |
| `SetCredentialEncrypted=` | `ID:ENCRYPTED_VALUE` | Embed **secret** data encrypted via `systemd-creds` |

**Security:** `SetCredential=` is visible via D-Bus — only for non-sensitive data. Use `SetCredentialEncrypted=` or `LoadCredentialEncrypted=` for secrets.

Generate encrypted lines: `systemd-creds -p encrypt - - <<< "mysecret"`

---

## 16. System V Compatibility

### 16.1 UtmpIdentifier=

| Property | Value |
|----------|-------|
| Takes | 4-character string |
| Effect | Creates utmp/wtmp entry for service lifetime |
| Used by | getty implementations |

### 16.2 UtmpMode=

| Value | Entries created |
|-------|----------------|
| `init` (default) | INIT_PROCESS only |
| `login` | INIT_PROCESS + LOGIN_PROCESS |
| `user` | INIT_PROCESS + LOGIN_PROCESS + USER_PROCESS |

---

## 17. Environment Variables Set by the Manager

These are automatically set for spawned processes:

| Variable | Content | Added |
|----------|---------|-------|
| `$PATH` | Fixed: `/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin` | v208 |
| `$LANG` | System locale | |
| `$USER` | Always set | v208 |
| `$LOGNAME` | Set if `User=` + `SetLoginEnvironment=` | v208 |
| `$HOME` | Set if `User=` + `SetLoginEnvironment=` | v208 |
| `$SHELL` | Set if `User=` + `SetLoginEnvironment=` | v208 |
| `$INVOCATION_ID` | Unique 128-bit hex per runtime cycle | v232 |
| `$XDG_RUNTIME_DIR` | Runtime dir for user services or PAM-enabled system services | v208 |
| `$RUNTIME_DIRECTORY` | Path from `RuntimeDirectory=` | v244 |
| `$STATE_DIRECTORY` | Path from `StateDirectory=` | v244 |
| `$CACHE_DIRECTORY` | Path from `CacheDirectory=` | v244 |
| `$LOGS_DIRECTORY` | Path from `LogsDirectory=` | v244 |
| `$CONFIGURATION_DIRECTORY` | Path from `ConfigurationDirectory=` | v244 |
| `$CREDENTIALS_DIRECTORY` | Path to credentials directory | v247 |
| `$TMPDIR` | Set to `/tmp` in specific `PrivateTmp=disconnected` scenarios | v258 |
| `$MAINPID` | Main process PID (only for `ExecReload=` etc.) | v209 |
| `$MANAGERPID` | Per-user service manager PID | v208 |
| `$LISTEN_FDS` / `$LISTEN_PID` / `$LISTEN_FDNAMES` | Socket activation info | v208 |
| `$NOTIFY_SOCKET` | sd_notify() socket path | v229 |
| `$WATCHDOG_PID` / `$WATCHDOG_USEC` | Watchdog info | |
| `$SYSTEMD_EXEC_PID` | This process's PID | v248 |
| `$TERM` | Terminal type (if connected to TTY) | v209 |
| `$LOG_NAMESPACE` | Log namespace name | v246 |
| `$JOURNAL_STREAM` | Device:inode of journal connection | v231 |
| `$PIDFILE` | PID file path from `PIDFile=` | v242 |
| `$REMOTE_ADDR` / `$REMOTE_PORT` | Remote peer info (socket activation) | v220 |
| `$SERVICE_RESULT` | Service exit result (ExecStop/ExecStopPost only) | v232 |
| `$EXIT_CODE` / `$EXIT_STATUS` | Exit details (ExecStop/ExecStopPost only) | v232 |
| `$MONITOR_*` | Trigger info for OnFailure/OnSuccess handlers | v251 |
| `$MEMORY_PRESSURE_WATCH` / `$MEMORY_PRESSURE_WRITE` | Memory pressure monitoring | v254 |
| `$FDSTORE` | Max file descriptors for fd store | v254 |
| `$DEBUG_INVOCATION` | Set when `RestartMode=debug` and previous start failed | v257 |

---

## 18. Process Exit Codes

### 18.1 C Library Codes

| Code | Name | Meaning |
|------|------|---------|
| 0 | `EXIT_SUCCESS` | Success |
| 1 | `EXIT_FAILURE` | Generic failure |

### 18.2 LSB Codes

| Code | Name | Meaning |
|------|------|---------|
| 2 | `EXIT_INVALIDARGUMENT` | Invalid arguments |
| 3 | `EXIT_NOTIMPLEMENTED` | Unimplemented feature |
| 4 | `EXIT_NOPERMISSION` | Insufficient privileges |
| 5 | `EXIT_NOTINSTALLED` | Not installed |
| 6 | `EXIT_NOTCONFIGURED` | Not configured |
| 7 | `EXIT_NOTRUNNING` | Not running |

### 18.3 systemd-Specific Codes (200+)

| Code | Name | Setting that caused it |
|------|------|----------------------|
| 200 | `EXIT_CHDIR` | `WorkingDirectory=` |
| 201 | `EXIT_NICE` | `Nice=` |
| 202 | `EXIT_FDS` | File descriptor setup |
| 203 | `EXIT_EXEC` | `execve()` failed (missing binary) |
| 204 | `EXIT_MEMORY` | Memory shortage |
| 205 | `EXIT_LIMITS` | `LimitCPU=` etc. |
| 206 | `EXIT_OOM_ADJUST` | `OOMScoreAdjust=` |
| 207 | `EXIT_SIGNAL_MASK` | Signal mask |
| 208 | `EXIT_STDIN` | `StandardInput=` |
| 209 | `EXIT_STDOUT` | `StandardOutput=` |
| 210 | `EXIT_CHROOT` | `RootDirectory=`/`RootImage=` |
| 211 | `EXIT_IOPRIO` | `IOSchedulingClass=`/`IOSchedulingPriority=` |
| 212 | `EXIT_TIMERSLACK` | `TimerSlackNSec=` |
| 213 | `EXIT_SECUREBITS` | `SecureBits=` |
| 214 | `EXIT_SETSCHEDULER` | `CPUSchedulingPolicy=`/`CPUSchedulingPriority=` |
| 215 | `EXIT_CPUAFFINITY` | `CPUAffinity=` |
| 216 | `EXIT_GROUP` | `Group=`/`SupplementaryGroups=` |
| 217 | `EXIT_USER` | `User=`/`PrivateUsers=` |
| 218 | `EXIT_CAPABILITIES` | `CapabilityBoundingSet=`/`AmbientCapabilities=` |
| 219 | `EXIT_CGROUP` | Control group setup |
| 220 | `EXIT_SETSID` | Session creation |
| 221 | `EXIT_CONFIRM` | User cancelled (`systemd.confirm_spawn=`) |
| 222 | `EXIT_STDERR` | `StandardError=` |
| 224 | `EXIT_PAM` | `PAMName=` |
| 225 | `EXIT_NETWORK` | `PrivateNetwork=` |
| 226 | `EXIT_NAMESPACE` | `ReadOnlyPaths=`, `ProtectHostname=`, `PrivateIPC=` etc. |
| 227 | `EXIT_NO_NEW_PRIVILEGES` | `NoNewPrivileges=` |
| 228 | `EXIT_SECCOMP` | `SystemCallFilter=` |
| 229 | `EXIT_SELINUX_CONTEXT` | `SELinuxContext=` |
| 230 | `EXIT_PERSONALITY` | `Personality=` |
| 231 | `EXIT_APPARMOR_PROFILE` | `AppArmorProfile=` |
| 232 | `EXIT_ADDRESS_FAMILIES` | `RestrictAddressFamilies=` |
| 233 | `EXIT_RUNTIME_DIRECTORY` | `RuntimeDirectory=` |
| 235 | `EXIT_CHOWN` | Socket ownership (socket units) |
| 236 | `EXIT_SMACK_PROCESS_LABEL` | `SmackProcessLabel=` |
| 237 | `EXIT_KEYRING` | Kernel keyring |
| 238 | `EXIT_STATE_DIRECTORY` | `StateDirectory=` |
| 239 | `EXIT_CACHE_DIRECTORY` | `CacheDirectory=` |
| 240 | `EXIT_LOGS_DIRECTORY` | `LogsDirectory=` |
| 241 | `EXIT_CONFIGURATION_DIRECTORY` | `ConfigurationDirectory=` |
| 242 | `EXIT_NUMA_POLICY` | `NUMAPolicy=`/`NUMAMask=` |
| 243 | `EXIT_CREDENTIALS` | Credentials setup |
| 245 | `EXIT_BPF` | `RestrictFileSystems=` |

---

## 19. Hardened Service Template for ASUS B460M-A

Drop-in file: `/etc/systemd/system/myservice.service.d/90-hardened.conf`

```ini
# ============================================================
# HARDENED SERVICE TEMPLATE — ASUS PRIME B460M-A / i7-10700
# systemd 260.1 — systemd.exec(5) per-service sandboxing
#
# Apply via:
#   sudo systemctl edit myservice.service
# Or create as drop-in at:
#   /etc/systemd/system/myservice.service.d/90-hardened.conf
# ============================================================

[Service]
# --- User Isolation ---
# DynamicUser=yes              # Uncomment if service has no state
User=myservice
Group=myservice

# --- Filesystem Protection ---
ProtectSystem=strict
ProtectHome=yes
PrivateTmp=yes
PrivateDevices=yes
PrivateMounts=yes
ProtectProc=invisible
ProcSubset=pid

# --- Write paths (customise per service) ---
# StateDirectory=myservice
# RuntimeDirectory=myservice
# LogsDirectory=myservice
# ReadWritePaths=/var/lib/myservice

# --- Kernel Protection ---
ProtectKernelTunables=yes
ProtectKernelModules=yes
ProtectKernelLogs=yes
ProtectControlGroups=yes
ProtectClock=yes
ProtectHostname=yes

# --- Namespace Isolation ---
PrivateNetwork=no              # Set yes if no networking needed
PrivateIPC=yes
PrivateUsers=yes
RestrictNamespaces=yes
LockPersonality=yes

# --- Privilege Restrictions ---
NoNewPrivileges=yes
RestrictSUIDSGID=yes
RestrictRealtime=yes
RemoveIPC=yes
MemoryDenyWriteExecute=yes

# --- System Call Filtering ---
SystemCallArchitectures=native
SystemCallFilter=@system-service
SystemCallFilter=~@privileged @resources @mount @clock @debug @module @raw-io @reboot @swap @obsolete @cpu-emulation
SystemCallErrorNumber=EPERM

# --- Network Restrictions ---
RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6
# RestrictAddressFamilies=AF_UNIX   # Use this for no-network services

# --- Capabilities ---
CapabilityBoundingSet=~CAP_SYS_ADMIN CAP_SYS_PTRACE CAP_SYS_MODULE CAP_SYS_RAWIO CAP_NET_ADMIN CAP_SYS_BOOT CAP_SYS_TIME CAP_MKNOD CAP_SYS_CHROOT CAP_AUDIT_CONTROL CAP_AUDIT_WRITE CAP_SYSLOG CAP_WAKE_ALARM

# --- Resource Limits ---
LimitCORE=0
LimitNOFILE=1024:4096
UMask=0077

# --- Logging ---
LogLevelMax=info

# --- Process Properties ---
KeyringMode=private
OOMScoreAdjust=0

# --- BPF ---
PrivateBPF=yes
```

### How to Apply to Existing Services

```bash
# Create a drop-in for an existing service (e.g., nginx)
sudo mkdir -p /etc/systemd/system/nginx.service.d/
sudo cp 90-hardened.conf /etc/systemd/system/nginx.service.d/

# Customise for nginx:
# - Remove PrivateNetwork=no → must stay no for web server
# - Add ReadWritePaths= for cache/log dirs
# - Relax MemoryDenyWriteExecute if using Lua/JIT

sudo systemctl daemon-reload
sudo systemctl restart nginx

# Verify what's applied:
systemd-analyze security nginx.service
```

### Verify Hardening Score

```bash
# Score all services (lower = better hardened)
systemd-analyze security

# Score a specific service with full details
systemd-analyze security myservice.service
```

---

## Appendix A: Quick-Reference Table — All Options

| # | Option | Section | Default | Hardened Value | Added |
|---|--------|---------|---------|---------------|-------|
| 1 | `ExecSearchPath=` | Paths | (unset) | — | v250 |
| 2 | `WorkingDirectory=` | Paths | `/` | — | |
| 3 | `RootDirectory=` | Paths | (unset) | — | |
| 4 | `RootImage=` | Paths | (unset) | — | v233 |
| 5 | `RootImageOptions=` | Paths | (unset) | — | v247 |
| 6 | `RootEphemeral=` | Paths | false | — | v254 |
| 7 | `RootHash=` | Paths | (unset) | — | v246 |
| 8 | `RootHashSignature=` | Paths | (unset) | — | v246 |
| 9 | `RootVerity=` | Paths | (unset) | — | v246 |
| 10 | `RootImagePolicy=` | Paths | (full chain) | — | v254 |
| 11 | `MountImagePolicy=` | Paths | (full chain) | — | v254 |
| 12 | `ExtensionImagePolicy=` | Paths | (root+usr) | — | v254 |
| 13 | `RootMStack=` | Paths | (unset) | — | v260 |
| 14 | `MountAPIVFS=` | Paths | false | — | v233 |
| 15 | `BindLogSockets=` | Paths | false | — | v257 |
| 16 | `ProtectProc=` | Paths | `default` | `invisible` | v247 |
| 17 | `ProcSubset=` | Paths | `all` | `pid` | v247 |
| 18 | `BindPaths=` | Paths | (unset) | — | v233 |
| 19 | `BindReadOnlyPaths=` | Paths | (unset) | — | v233 |
| 20 | `MountImages=` | Paths | (unset) | — | v247 |
| 21 | `ExtensionImages=` | Paths | (unset) | — | v248 |
| 22 | `ExtensionDirectories=` | Paths | (unset) | — | v251 |
| 23 | `User=` | Identity | `root` | (dedicated user) | |
| 24 | `Group=` | Identity | (user's group) | (dedicated group) | |
| 25 | `DynamicUser=` | Identity | false | `yes` (if stateless) | v232 |
| 26 | `SupplementaryGroups=` | Identity | (unset) | — | |
| 27 | `SetLoginEnvironment=` | Identity | (auto) | — | v255 |
| 28 | `PAMName=` | Identity | (unset) | — | |
| 29 | `CapabilityBoundingSet=` | Capabilities | (full) | `~CAP_SYS_ADMIN...` | |
| 30 | `AmbientCapabilities=` | Capabilities | (empty) | — | v229 |
| 31 | `NoNewPrivileges=` | Security | false | `yes` | v187 |
| 32 | `SecureBits=` | Security | 0 | — | |
| 33 | `SELinuxContext=` | MAC | (unset) | — | v209 |
| 34 | `AppArmorProfile=` | MAC | (unset) | — | v210 |
| 35 | `SmackProcessLabel=` | MAC | (unset) | — | v218 |
| 36 | `LimitCPU=` | Limits | (default) | — | |
| 37 | `LimitFSIZE=` | Limits | (default) | — | |
| 38 | `LimitDATA=` | Limits | (default) | — | |
| 39 | `LimitSTACK=` | Limits | (default) | — | |
| 40 | `LimitCORE=` | Limits | (default) | `0` | |
| 41 | `LimitRSS=` | Limits | (default) | — | |
| 42 | `LimitNOFILE=` | Limits | (default) | `1024:4096` | |
| 43 | `LimitAS=` | Limits | (default) | — | |
| 44 | `LimitNPROC=` | Limits | (default) | — | |
| 45 | `LimitMEMLOCK=` | Limits | (default) | — | |
| 46 | `LimitLOCKS=` | Limits | (default) | — | |
| 47 | `LimitSIGPENDING=` | Limits | (default) | — | |
| 48 | `LimitMSGQUEUE=` | Limits | (default) | — | |
| 49 | `LimitNICE=` | Limits | (default) | — | |
| 50 | `LimitRTPRIO=` | Limits | (default) | — | |
| 51 | `LimitRTTIME=` | Limits | (default) | — | |
| 52 | `UMask=` | Process | 0022 | `0077` | |
| 53 | `CoredumpFilter=` | Process | (inherited) | — | v246 |
| 54 | `KeyringMode=` | Process | `private` | `private` | v235 |
| 55 | `OOMScoreAdjust=` | Process | 0 | — | |
| 56 | `TimerSlackNSec=` | Process | (inherited) | — | |
| 57 | `Personality=` | Process | (host) | — | v209 |
| 58 | `IgnoreSIGPIPE=` | Process | true | — | |
| 59 | `Nice=` | Scheduling | (inherited) | — | |
| 60 | `CPUSchedulingPolicy=` | Scheduling | `other` | — | |
| 61 | `CPUSchedulingPriority=` | Scheduling | (default) | — | |
| 62 | `CPUSchedulingResetOnFork=` | Scheduling | false | — | |
| 63 | `CPUAffinity=` | Scheduling | (unset) | — | |
| 64 | `NUMAPolicy=` | Scheduling | (default) | — | v243 |
| 65 | `NUMAMask=` | Scheduling | (unset) | — | v243 |
| 66 | `IOSchedulingClass=` | Scheduling | `best-effort` | — | |
| 67 | `IOSchedulingPriority=` | Scheduling | 4 | — | |
| 68 | `ProtectSystem=` | Sandboxing | false | `strict` | v214 |
| 69 | `ProtectHome=` | Sandboxing | false | `yes` | v214 |
| 70 | `RuntimeDirectory=` | Sandboxing | (unset) | (service-specific) | v211 |
| 71 | `StateDirectory=` | Sandboxing | (unset) | (service-specific) | v211 |
| 72 | `CacheDirectory=` | Sandboxing | (unset) | (service-specific) | v211 |
| 73 | `LogsDirectory=` | Sandboxing | (unset) | (service-specific) | v211 |
| 74 | `ConfigurationDirectory=` | Sandboxing | (unset) | (service-specific) | v211 |
| 75 | `RuntimeDirectoryMode=` | Sandboxing | 0755 | — | v234 |
| 76 | `StateDirectoryMode=` | Sandboxing | 0755 | — | v234 |
| 77 | `CacheDirectoryMode=` | Sandboxing | 0755 | — | v234 |
| 78 | `LogsDirectoryMode=` | Sandboxing | 0755 | — | v234 |
| 79 | `ConfigurationDirectoryMode=` | Sandboxing | 0755 | — | v234 |
| 80 | `StateDirectoryQuota=` | Sandboxing | off | — | v258 |
| 81 | `CacheDirectoryQuota=` | Sandboxing | off | — | v258 |
| 82 | `LogsDirectoryQuota=` | Sandboxing | off | — | v258 |
| 83 | `StateDirectoryAccounting=` | Sandboxing | false | — | v258 |
| 84 | `CacheDirectoryAccounting=` | Sandboxing | false | — | v258 |
| 85 | `LogsDirectoryAccounting=` | Sandboxing | false | — | v258 |
| 86 | `RuntimeDirectoryPreserve=` | Sandboxing | `no` | — | v235 |
| 87 | `TimeoutCleanSec=` | Sandboxing | infinity | — | v244 |
| 88 | `ReadWritePaths=` | Sandboxing | (unset) | — | v231 |
| 89 | `ReadOnlyPaths=` | Sandboxing | (unset) | — | v231 |
| 90 | `InaccessiblePaths=` | Sandboxing | (unset) | — | v231 |
| 91 | `ExecPaths=` | Sandboxing | (unset) | — | v231 |
| 92 | `NoExecPaths=` | Sandboxing | (unset) | — | v231 |
| 93 | `TemporaryFileSystem=` | Sandboxing | (unset) | — | v238 |
| 94 | `PrivateTmp=` | Sandboxing | false | `yes` | |
| 95 | `PrivateDevices=` | Sandboxing | false | `yes` | v209 |
| 96 | `PrivateNetwork=` | Sandboxing | false | (service-specific) | |
| 97 | `PrivateUsers=` | Sandboxing | false | `yes` | v232 |
| 98 | `PrivatePIDs=` | Sandboxing | false | — | v257 |
| 99 | `PrivateIPC=` | Sandboxing | false | `yes` | v248 |
| 100 | `PrivateMounts=` | Sandboxing | false | (implied) | v239 |
| 101 | `PrivateBPF=` | Sandboxing | false | `yes` | v258 |
| 102 | `UserNamespacePath=` | Sandboxing | (unset) | — | v259 |
| 103 | `NetworkNamespacePath=` | Sandboxing | (unset) | — | v242 |
| 104 | `IPCNamespacePath=` | Sandboxing | (unset) | — | v248 |
| 105 | `ProtectHostname=` | Sandboxing | false | `yes` | v242 |
| 106 | `ProtectClock=` | Sandboxing | false | `yes` | v245 |
| 107 | `ProtectKernelTunables=` | Sandboxing | false | `yes` | v232 |
| 108 | `ProtectKernelModules=` | Sandboxing | false | `yes` | v232 |
| 109 | `ProtectKernelLogs=` | Sandboxing | false | `yes` | v244 |
| 110 | `ProtectControlGroups=` | Sandboxing | false | `yes` | v232 |
| 111 | `MemoryKSM=` | Sandboxing | (unset) | — | v254 |
| 112 | `MemoryTHP=` | Sandboxing | `inherit` | — | v260 |
| 113 | `MountFlags=` | Sandboxing | `shared` | (don't change) | |
| 114 | `RestrictAddressFamilies=` | Restrict | (all) | `AF_UNIX AF_INET AF_INET6` | v211 |
| 115 | `RestrictFileSystems=` | Restrict | (all) | — | v250 |
| 116 | `RestrictNamespaces=` | Restrict | false | `yes` | v233 |
| 117 | `DelegateNamespaces=` | Restrict | false | — | v258 |
| 118 | `LockPersonality=` | Restrict | false | `yes` | v235 |
| 119 | `MemoryDenyWriteExecute=` | Restrict | false | `yes` | v231 |
| 120 | `RestrictRealtime=` | Restrict | false | `yes` | v231 |
| 121 | `RestrictSUIDSGID=` | Restrict | false | `yes` | v242 |
| 122 | `RemoveIPC=` | Restrict | false | `yes` | v232 |
| 123 | `SystemCallFilter=` | Syscall | (all) | `@system-service` | v187 |
| 124 | `SystemCallErrorNumber=` | Syscall | `kill` | `EPERM` | v209 |
| 125 | `SystemCallArchitectures=` | Syscall | (all) | `native` | v209 |
| 126 | `SystemCallLog=` | Syscall | (none) | — | v247 |
| 127 | `Environment=` | Env | (empty) | — | |
| 128 | `EnvironmentFile=` | Env | (unset) | — | |
| 129 | `PassEnvironment=` | Env | (empty) | — | v228 |
| 130 | `UnsetEnvironment=` | Env | (empty) | — | v235 |
| 131 | `StandardInput=` | I/O | `null` | — | |
| 132 | `StandardOutput=` | I/O | `journal` | — | |
| 133 | `StandardError=` | I/O | `inherit` | — | |
| 134 | `StandardInputText=` | I/O | (unset) | — | v236 |
| 135 | `StandardInputData=` | I/O | (unset) | — | v236 |
| 136 | `LogLevelMax=` | Logging | (unset) | `info` | v236 |
| 137 | `LogExtraFields=` | Logging | (empty) | — | v236 |
| 138 | `LogRateLimitIntervalSec=` | Logging | (journald default) | — | v240 |
| 139 | `LogRateLimitBurst=` | Logging | (journald default) | — | v240 |
| 140 | `LogFilterPatterns=` | Logging | (unset) | — | v253 |
| 141 | `LogNamespace=` | Logging | (default) | — | v245 |
| 142 | `SyslogIdentifier=` | Logging | (process name) | — | |
| 143 | `SyslogFacility=` | Logging | `daemon` | — | |
| 144 | `SyslogLevel=` | Logging | `info` | — | |
| 145 | `SyslogLevelPrefix=` | Logging | true | — | |
| 146 | `TTYPath=` | TTY | `/dev/console` | — | |
| 147 | `TTYReset=` | TTY | false | — | |
| 148 | `TTYVHangup=` | TTY | false | — | |
| 149 | `TTYColumns=` | TTY | (auto) | — | v250 |
| 150 | `TTYRows=` | TTY | (auto) | — | v250 |
| 151 | `TTYVTDisallocate=` | TTY | false | — | |
| 152 | `LoadCredential=` | Credentials | (unset) | — | v247 |
| 153 | `LoadCredentialEncrypted=` | Credentials | (unset) | — | v247 |
| 154 | `ImportCredential=` | Credentials | (unset) | — | v254 |
| 155 | `SetCredential=` | Credentials | (unset) | — | v247 |
| 156 | `SetCredentialEncrypted=` | Credentials | (unset) | — | v247 |
| 157 | `UtmpIdentifier=` | SysV | (unset) | — | |
| 158 | `UtmpMode=` | SysV | `init` | — | v225 |
| 159 | `BPFDelegateCommands=` | BPF | none | — | v258 |
| 160 | `BPFDelegateMaps=` | BPF | none | — | v258 |
| 161 | `BPFDelegatePrograms=` | BPF | none | — | v258 |
| 162 | `BPFDelegateAttachments=` | BPF | none | — | v258 |

**Total: 162 options documented.**

---

## Appendix B: Predefined System Call Sets

Use with `SystemCallFilter=@setname`. List actual contents with `systemd-analyze syscall-filter`.

| Set | Description |
|-----|-------------|
| `@aio` | Asynchronous I/O (io_setup, io_submit, etc.) |
| `@basic-io` | Read, write, seek, dup, close |
| `@chown` | chown, fchownat, etc. |
| `@clock` | adjtimex, settimeofday — clock modification |
| `@cpu-emulation` | vm86 and related — CPU emulation |
| `@debug` | ptrace, perf_event_open — debugging/tracing |
| `@file-system` | open, create, rename, remove files/dirs |
| `@io-event` | poll, select, epoll, eventfd |
| `@ipc` | Pipes, SysV IPC, POSIX message queues |
| `@keyring` | keyctl and related — kernel keyring |
| `@memlock` | mlock, mlockall — lock memory in RAM |
| `@module` | init_module, delete_module — kernel modules |
| `@mount` | mount, chroot, umount — filesystem mounting |
| `@network-io` | Socket I/O (socket, connect, send, recv) |
| `@obsolete` | Unusual, obsolete, or unimplemented calls |
| `@pkey` | Memory protection keys (pkey_*) |
| `@privileged` | All calls requiring capabilities |
| `@process` | clone, kill, namespace operations |
| `@raw-io` | ioperm, iopl, pciconfig_read — raw I/O ports |
| `@reboot` | reboot, kexec |
| `@resources` | setrlimit, setpriority — resource changes |
| `@sandbox` | seccomp, Landlock — sandboxing |
| `@setuid` | setuid, setgid, setresuid — credential changes |
| `@signal` | signal, sigprocmask — signal handling |
| `@swap` | swapon, swapoff |
| `@sync` | fsync, msync — disk sync |
| `@system-service` | **Recommended starting point** — common service calls, excludes @clock @mount @swap @reboot |
| `@timer` | alarm, timer_create — scheduling by time |
| `@known` | All kernel-defined syscalls |

---

## Appendix C: Predefined Filesystem Sets

Use with `RestrictFileSystems=@setname`. List actual contents with `systemd-analyze filesystems`.

| Set | Description |
|-----|-------------|
| `@basic-api` | Basic filesystem API (proc, sysfs, etc.) |
| `@auxiliary-api` | Auxiliary filesystem API |
| `@common-block` | Common block device filesystems (ext4, xfs, btrfs, etc.) |
| `@historical-block` | Historical block device filesystems |
| `@network` | Well-known network filesystems (nfs, cifs, etc.) |
| `@privileged-api` | Privileged filesystem API |
| `@temporary` | Temporary filesystems (tmpfs, ramfs) |
| `@known` | All kernel-defined filesystems |

---

## Related Reports

| Report | Topic | Status |
|--------|-------|--------|
| **25** | systemd-system.conf(5) — System-wide defaults | ✅ Complete |
| **26** | systemd.exec(5) — Per-service execution (THIS REPORT) | ✅ Complete |
| **27** | systemd.resource-control(5) — Cgroup resource limits | 📋 Next |
| **28** | Kernel command-line hardening flags | 📋 Planned |
| **29** | Audit framework (auditd rules + systemd integration) | 📋 Planned |

---

*Report 27 of the masterhq investigation series. 162 options documented from systemd.exec(5) with per-option hardening recommendations for the ASUS PRIME B460M-A / i7-10700 system.*
