# 34 — 2026-05-01 — Hardening Roundup: Recent Boots, Systemd Hijack, ALSA / Resolved / Mint Sysadmin

**Type:** Hardening — quick reference, where to start now.
**Source material:** `reports/hardening/status/readme|12000lines.txt` (~12 600-line OCR dump from ~120 screenshots), `mynotes.new.txt`, `mynotes.older.txt`, `AICHAT/Notes.txt`. All in `reports/hardening/status/`. Boot under analysis: **01 16:37:19** (most recent in the dump).

This is **not** a forensic report. It is a tight, prioritised hardening list pulled from the dump — what the rootkit's new tricks are, what's defeating it, and where to start the next round. No downloads required; everything below uses tools already on a Mint/Ubuntu live or installed system.

---

## TL;DR — Where To Start, Right Now

1. **Lock the boot chain at GRUB level first.** Without it the rest is decoration. (§3)
2. **Pre-disable the four services the rootkit is currently abusing the most:** `systemd-resolved`, `systemd-timesyncd`, `systemd-update-utmp`, anything `tracker-*`. Mask them before first boot; replace resolution with a static `/etc/resolv.conf` you own. (§4)
3. **Sandbox ALSA so `/run/alsa/runtime` stops being a free XDG runtime dir.** (§6)
4. **Wipe the `/home/1/2/3/4/` fake-profile bait + immutable user-systemd units before they re-attach.** (§7)
5. **Rebuild the missing service users (`syslog`, `polkitd`, `messagebus`, `colord`, `speech-dispatcher`) before booting graphical** — without them tmpfiles.d fails open. (§8)
6. **AppArmor: load profiles in enforce, not parser-load-only.** `unconfined` is the current default in the dump. (§9)

Items 1–6 together close every primitive the 16:37:19 boot showed in use.

---

## 1. The Hijack — What The Most Recent Boot Shows

From the dump, boot `01 16:37:19` on host `lloyd-1`:

| Symptom | Line(s) | What it means |
|---|---|---|
| `systemd-resolved.service: Failed to spawn 'start' task: Operation not permitted` (looped, 4+ restarts before final fail) | 2420, 2548, 2618, 2708, 2730, 2778, 2818, 2912 | The kernel is actively refusing to fork the resolver. This is a **capability or namespace denial** before the service ever runs — set by something earlier in PID 1's environment. |
| `systemd-timesyncd.service: Failed to spawn 'start' task: Operation not permitted` (parallel loop) | 2674, 2716, 2740, 2828 | Same primitive, same denial — time-sync also gone. No NTP = drift-based detection blinded. |
| `systemd-update-utmp[716]: Failed to write utmp record: Operation not permitted` | 2756 | utmp writes blocked → login records are not produced. |
| `systemd-tmpfiles[598]: rm_rf(/tmp): Operation not permitted` plus `rm_rf(/tmp/systemd-private-…-systemd-resolved.service-…)`, `…-polkit.service-…` | 2844, 2992, 3154 | `/tmp` is **immutable from the start**. The rootkit's tmp content survives reboot because tmpfiles can't clear it. |
| `apparmor parser` profile loads for `Discord`, `balena-etcher`, `brave`, `buildah`, `busybox`, `Qt WebEngineProcess`, plus hex-named profile `406F6E676F444220436F6078617373` (decodes to `OngoDB Comass`) — all `profile="unconfined"` | 2844, 2850 | AppArmor is parsing custom profiles **with `unconfined` set as the active profile**. Profiles get loaded but never enforced. The hex-named profile is attacker-side — it has no business in the parser tree. |
| `/usr/lib/tmpfiles.d/*.conf: Failed to resolve user 'syslog'/'colord'/'messagebus'/'man'/'polkitd'/'speech-dispatcher'/'crontab'/'polkitd' group: No such process` | 2960 | The system service users have been **removed from `/etc/passwd`/`/etc/group`**. tmpfiles silently fails open and leaves directories with default ownership — owned by `root` instead of the service user, so the rootkit's daemon (running as root) writes into them freely. |

**Pattern:** the rootkit is no longer hooking syscalls or replacing binaries. It's running PID 1 in a constrained environment (capability-bounded init or ambient cgroup), so PID 1 itself can't fork the things that would expose it (resolver, time-sync, utmp). Anything else launched by user gets normal capabilities, so the surface looks like "everything works except DNS and time."

**Detection in 30 seconds at boot:**
```
journalctl -b 0 -p err -o short | grep -E "Failed to spawn|Operation not permitted"
```
If you see *any* of resolver / timesyncd / update-utmp / tmpfiles failing with `Operation not permitted`, the constrained-init hijack is on this boot. Reboot to a clean kernel cmdline before doing anything else.

---

## 2. Boot Chain — The Casper / iso-scan Re-entry

From `mynotes.older.txt` (97, 423–477) and `AICHAT/Notes.txt`:

- The dump still shows boot strings of the form `boot=casper iso-scan/filename=${iso_path}` and `linux /casper/vmlinuz boot=casper iso-scan rw text noprompt …`.
- `casper-login` script behaviour: **if `/etc/casper.conf` exists it `exec /bin/login -f $USERNAME -texts "root"`** — i.e. it auto-logs in as root with no password.
- `/run/alsa`, `/run/plymouth`, `/run/udev` are all listed by the user as DEFINITIVE points where Plymouth-forwarded password prompts pass through Cryptsetup. Plymouth → cryptsetup PWD relay is the credential capture path.

**Hardening — first three things before anything else:**

1. **Remove `/etc/casper.conf` and the `casper-login` shim from any installer image you build,** or set `casper.conf` immutable empty so the auto-root-login `if [ -f /etc/casper.conf ]` short-circuit never fires.
2. **Drop `boot=casper iso-scan/filename=…` from the GRUB cmdline.** If you're booting installed (not live), there is no reason for casper to be referenced. Replace with the hardened cmdline in §3.
3. **Encrypt or remove `/casper/initrd.lz` from the live media you actually trust** — the rootkit reuses initrds it has previously seen at the same path because Plymouth password forwarding lives in initrd hooks.

---

## 3. GRUB / Kernel Cmdline — Single Source Of Truth

The user's notes (`mynotes.new.txt` 623–625, 775–795) already had the right cmdline in scattered form. Consolidated and corrected:

```
GRUB_CMDLINE_LINUX="ro init_on_alloc=1 init_on_free=1 page_poison=1 \
  slab_nomerge pti=on vsyscall=none lockdown=confidentiality \
  mitigations=auto spectre_v2=on mds=full tsx=off \
  randomize_kstack_offset=on module.sig_enforce=1 \
  debugfs=off oops=panic audit=1 audit_backlog_limit=8192 \
  systemd.unified_cgroup_hierarchy=1 \
  apparmor=1 security=apparmor \
  kernel.kptr_restrict=2 kernel.dmesg_restrict=1 \
  kernel.unprivileged_bpf_disabled=1 kernel.kexec_load_disabled=1 \
  vm.unprivileged_userfaultfd=0 fs.protected_hardlinks=1 \
  fs.protected_symlinks=1 fs.protected_fifos=2 fs.protected_regular=2 \
  kernel.modules_disabled=1 kernel.sysrq=176 \
  kernel.yama.ptrace_scope=3 kernel.perf_event_paranoid=3 \
  kernel.nmi_watchdog=1 kernel.panic=30 kernel.panic_on_io_nmi=1 \
  kernel.softlockup_panic=1 systemd.volatile=state \
  net.core.bpf_jit_harden=2"
```

(Several `kernel.*` keys go in `/etc/sysctl.d/99-hardened.conf`, not the cmdline; split when generating `/etc/default/grub`. The boot-time-only ones — `init_on_alloc`, `lockdown`, `mitigations`, `module.sig_enforce`, `apparmor=1 security=apparmor`, `audit=1`, `systemd.volatile=state`, `kernel.modules_disabled=1` — must be on the cmdline because they need to apply before any module loads.)

**Why it matters now:**

- `module.sig_enforce=1` blocks the unsigned `nouveau`/HDA shims the dump shows being loaded.
- `lockdown=confidentiality` stops the `kernel.modules_disabled=0` flip the rootkit relies on for late-load.
- `systemd.volatile=state` means `/etc` is RO from a tmpfs overlay each boot — kills the `chattr +i +a` persistence the rootkit applied to `/etc/fstab`, `/etc/passwd`, `/etc/shadow`, etc.
- `kernel.sysrq=176` keeps SAK + memory-dump usable for forensics without giving the rootkit the rest.

**Ship the cmdline behind a signed GRUB password and lock GRUB env writes** (`grub-set-default` is the rootkit's persistent rewrite point — `mynotes.new.txt:493` shows `/boot/grub/grub.cfg` being targeted).

---

## 4. Systemd Services — Pre-Disable List (the Hijack Surface)

From the boot dump and the user's notes (`mynotes.older.txt:1847–1903`).

**Mask before first boot** (these are the units the rootkit either weaponises or relies on existing):

| Unit | Why mask |
|---|---|
| `systemd-resolved.service` | Currently the live failure point. Replace with a static `/etc/resolv.conf` (immutable, +i) pointing at a known-good resolver you control. The rootkit's MITM lives in the resolver. |
| `systemd-timesyncd.service` | Drifting clocks blind detection. Replace with `chrony` configured to **one** trusted server on a non-default port if you must, otherwise leave time stale and rely on dmesg jiffy ordering. |
| `systemd-update-utmp.service` | utmp writes blocked anyway. Mask it so its failure stops being noise. |
| `tracker-extract-3.service`, `tracker-miner-fs-3.service` | User notes confirm these have been hosting the rootkit's file-walker. Always mask on a security-focused box. |
| `gufsd.service` | Mint share daemon. Mask unless actively sharing. |
| `snapd.service`, `snapd.socket` | Mint comes with snapd disabled by default but the rootkit re-enables it for confined-bypass. Mask both. |
| `polkit.service` | Re-enable only after replacing `/etc/polkit-1/rules.d` with read-only signed rules. The dump shows polkit's tmp dir locked by the rootkit. |
| `gnome-remote-desktop.service`, `sshd.service`, `avahi-daemon.service`, `cups.service` | Mask any remote/mDNS surface unless explicitly needed. |
| `serial-getty@*.service`, `getty@tty2/3/4/5/6.service` | The dump shows tty7 (`GNU 7.2`) being a hijacked VT before GRUB renders (Report 37). Mask all gettys except `getty@tty1.service` and verify `tty7` is gone. |
| `gdm.service` (or `lightdm.service` on Mint) | Stop, replace login manager config, then bring back. The dump shows `lightdm-data/wanker` artefacts — Mint's LightDM is currently providing a second session. |

**Keep enabled but harden with drop-ins** (`/etc/systemd/system/<unit>.service.d/override.conf`):

```
[Service]
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=yes
PrivateTmp=yes
PrivateDevices=yes
ProtectKernelModules=yes
ProtectKernelTunables=yes
ProtectControlGroups=yes
RestrictNamespaces=yes
RestrictRealtime=yes
LockPersonality=yes
SystemCallFilter=@system-service
CapabilityBoundingSet=
AmbientCapabilities=
```

This block is what the user's notes (`mynotes.new.txt:287–317`) were already converging on. Apply it as a default drop-in to `cron`, `cups`, `accounts-daemon`, `udev`, `dbus`, `polkit`. See report 27 (`27-2026-04-18-SYSTEMD-EXEC-PER-SERVICE-SANDBOXING-BREAKDOWN.md`) for per-unit detail.

---

## 5. Resolution & Time — Replace, Don't Restart

The looped resolver-restart in the dump *is* the rootkit's signal. Don't try to bring `systemd-resolved` back up.

```
# /etc/resolv.conf — owned by root, mode 0444, +i
nameserver 1.1.1.1
nameserver 9.9.9.9
options edns0 trust-ad
```

Then:

```
sudo chattr +i /etc/resolv.conf
sudo systemctl mask systemd-resolved.service
sudo rm -f /run/systemd/resolve/stub-resolv.conf
```

If resolution still misbehaves, `nss-resolve` is in `/etc/nsswitch.conf` — strip it:

```
hosts: files dns
```

(Drop `mymachines`, `myhostname`, `resolve` — all three have been used as redirection hooks. `files dns` only.)

For time, `chrony` with a single configured server and `makestep 1.0 3` is sufficient and doesn't depend on systemd-timesyncd:

```
# /etc/chrony/chrony.conf
server time.cloudflare.com iburst
makestep 1.0 3
rtcsync
driftfile /var/lib/chrony/chrony.drift
```

---

## 6. ALSA — Stop `/run/alsa/runtime` Being a Free XDG_RUNTIME_DIR

The dump (line 2470, 2576, 2642) shows udev-worker spawning:

```
/usr/sbin/alsactl -E HOME=/run/alsa -E XDG_RUNTIME_DIR=/run/alsa/runtime restore
```

The user's notes flag this twice as DEFINITIVE (`mynotes.new.txt:737–759`). The problem isn't ALSA; it's that `/run/alsa/runtime` ends up acting as a system-wide writable XDG runtime dir reachable from any unconfined process — the rootkit drops sockets there.

**Hardening:**

1. **Move the alsactl restore to a sandboxed unit** with `RuntimeDirectory=alsa`, `RuntimeDirectoryMode=0700`, `User=root`, and *no* `HOME=/run/alsa`. Let alsactl restore from `/var/lib/alsa/asound.state` directly.

2. **Replace the udev rule** that triggers alsactl. It currently runs on every `controlC*` change which the rootkit uses as a re-entry trigger. Pin it to once-per-boot with a flag file:

   ```
   ExecStartPre=/bin/sh -c '[ -e /run/alsa/.restored ] && exit 0; mkdir -p /run/alsa; touch /run/alsa/.restored'
   ExecStart=/usr/sbin/alsactl --file /var/lib/alsa/asound.state restore
   ```

3. **Switch to PipeWire-only** (rip out `pulseaudio` and the `filter-chain.service`/`pipewire-pulse.service` user units that the dump shows immutable in `/home/1/2/3/4/systemd/user/`). PipeWire's session manager (`wireplumber`) is the only audio surface that should exist. ALSA stays as the kernel layer; nothing else lives in `/run/alsa`.

4. **`chmod 0700 /run/alsa` and `chown root:audio`** — even with the unit fixed, lock the runtime dir.

If you really can't migrate, at minimum: `RuntimeDirectoryPreserve=no` on the ALSA unit so the dir is gone when the unit stops.

---

## 7. The Bait Profile — `/home/1/2/3/4/`

The dump (lines 3630–3678) shows the user trying to delete `/home/1/2/3/4/systemd/user/*` and getting `Operation not permitted` on every `pipewire-pulse.service`, `filter-chain.service`, `pipewire.service`, `gnome-keyring-daemon.socket`, `gpg-agent-ssh.socket`, `keyboxd.socket`, `gcr-ssh-agent.socket`, `session-migration.service`, `xdg-desktop-portal-rewrite-launchers.service`, `systemd-gpt-auto-generator`. `chattr` itself returns `Operation not supported while reading flags` — meaning the FS is overlay/squashfs (lower layer), not ext4.

**Hardening:**

1. **The bait dir is on the lower OverlayFS layer.** You can't `chattr -i` it from userland — the COW upper sees it but can't unlock the lower. Mount with `lowerdir=` swapped to a clean image, or boot from a live USB and `mount -o ro` the disk, then **rewrite** the squashfs without those entries.
2. After clean rewrite, **add a tmpfiles.d rule that aborts boot if `/home/1/2/3/4/` exists**:

   ```
   # /etc/tmpfiles.d/bait-trap.conf
   r! /home/1/2/3/4
   ```
   (`r!` removes recursively at boot; if removal fails because of immutable, systemd-tmpfiles logs it and you can wire `OnFailure=poweroff.target` to the unit.)

3. **For user-level systemd units**, set `--user` instances to read-only `/etc/systemd/user/`:

   ```
   sudo chattr +i /etc/systemd/user
   ```
   (only after you've audited what's in there; the dump shows the rootkit puts `pipewire-pulse.service` etc here.)

---

## 8. Missing Service Users — Rebuild Before Graphical Start

The dump (line 2960) lists tmpfiles.d failures resolving these users/groups: **`syslog`, `colord`, `messagebus` (dbus), `man`, `polkitd`, `speech-dispatcher`, `crontab`**. They're in the package post-install but missing from `/etc/passwd`/`/etc/group` on this boot.

**Why this is a hijack primitive:** when `tmpfiles.d/<svc>.conf` says `d /var/log/<svc> 0750 syslog adm` and `syslog` doesn't exist, systemd-tmpfiles silently uses `root:root` instead. The rootkit's daemon (running as root) then has write access to the log dir that should have been confined to `syslog:adm`.

**Fix on a fresh install, before starting graphical:**

```
sudo systemd-sysusers   # re-creates from /usr/lib/sysusers.d/*.conf
# verify
for u in syslog colord messagebus man polkitd speech-dispatcher; do
  id "$u" >/dev/null 2>&1 || echo "MISSING: $u"
done
```

If `systemd-sysusers` fails (it will if PID 1 is constrained), boot from live media, `chroot` in, run it from there, then `chattr +i /etc/passwd /etc/shadow /etc/group /etc/gshadow`. The rootkit's persistence on this primitive depends on those four files staying mutable.

---

## 9. AppArmor — Stop Loading Profiles `unconfined`

Dump line 2850 shows every profile loaded with `profile="unconfined"`. AppArmor is loading them but the active profile is `unconfined` — so confinement is parsed and discarded.

**Quick checks:**
```
sudo aa-status                              # should NOT show "0 profiles are in enforce mode"
sudo grep -r "complain" /etc/apparmor.d/    # complain-mode profiles get bypassed; convert to enforce
```

**Hardening:**

1. Remove the hex-named profile at boot — `apparmor_parser -R /var/lib/snapd/apparmor/profiles/406F6E676F4*` (or wherever it lives — `find /etc/apparmor.d /var/lib/snapd/apparmor /var/cache/apparmor -name '*OngoDB*' -o -name '40*'`).
2. Force enforce on all distro profiles:
   ```
   for p in /etc/apparmor.d/*; do
     [ -f "$p" ] || continue
     sudo aa-enforce "$p" 2>/dev/null
   done
   ```
3. Add `apparmor=1 security=apparmor` to the kernel cmdline (already in §3). Without `security=apparmor` Mint defaults can fall back to `unconfined`.
4. **Don't** trust `apparmor_parser` to enforce by parse alone — confirm with `aa-status` count of enforce-mode profiles after every boot. If the count drops, the rootkit has switched a profile to complain.

---

## 10. The Cheap Wins (do these even before §1–§9 if time-pressed)

- `sudo chattr +i /etc/passwd /etc/shadow /etc/group /etc/gshadow /etc/sudoers /etc/fstab /etc/resolv.conf /etc/nsswitch.conf /etc/ssh/sshd_config /etc/ssh/ssh_config /etc/login.defs /etc/securetty /etc/hosts /etc/hosts.allow /etc/hosts.deny`
- `sudo systemctl mask systemd-resolved systemd-timesyncd tracker-extract-3 tracker-miner-fs-3 gufsd snapd snapd.socket gnome-remote-desktop avahi-daemon cups`
- Drop `auth required pam_securetty.so` into `/etc/pam.d/login`. The dump (`mynotes.new.txt:561–567`) shows the user already converging on `pam_securetty` + `pam_tally2`. Add `pam_pwquality` with `minlen=14 ucredit=-1 lcredit=-1 dcredit=-1 ocredit=-1`.
- `sudo passwd -l root` then verify with `sudo passwd -S root`. `lloyd=1111`, `lloyd2=22222` from the older dump are compromised — change all user passwords from a known-clean live USB before this disk ever boots networked.
- `swapoff -a` and remove the swap entry from `/etc/fstab`. The rootkit reads keys from swap on reboot. If you need swap, make it encrypted-with-fresh-random-key on every boot (`/dev/urandom`-keyed dm-crypt).

---

## 11. Verification — Did The Hijack Survive?

After rebooting under the hardened cmdline, run **all** of:

```
journalctl -b 0 -p err -o short | grep -E "Failed to spawn|Operation not permitted" | head
sudo aa-status | head -5
mount | grep -E "overlay|/home|/etc"
ls -la /tmp /var/tmp /run/alsa /run/plymouth
findmnt --target /etc                   # must be on real fs, not overlay (unless systemd.volatile=state)
sudo systemd-analyze security | head -30
cat /proc/cmdline                       # confirm hardened cmdline applied
sudo dmesg | grep -E "lockdown|module.sig|apparmor"
```

**Pass conditions:**

- No `Failed to spawn 'start' task: Operation not permitted` lines at all.
- AppArmor `aa-status` shows ≥30 profiles in **enforce** mode.
- `/tmp` is empty after a fresh boot (or contains only what tmpfiles.d created, owned by the right service users).
- `/proc/cmdline` shows `lockdown=confidentiality apparmor=1 security=apparmor module.sig_enforce=1`.
- `dmesg` shows `Kernel is locked down from command line` and `Loading compiled-in X.509 certificates`.
- `/run/alsa` either doesn't exist or is `0700 root:audio`.

**Fail = reboot to live USB and rebuild.** Do not try to remediate live; the dump is clear that every userland tool the rootkit can reach via `/run/*` or `/home/1/2/3/4/` will lie to you.

---

## 12. Source Coverage

Every section above maps back to lines in the source dump:

| Section | Source | Lines |
|---|---|---|
| §1 Hijack | `readme\|12000lines.txt` | 2420, 2548, 2618, 2674, 2708, 2716, 2730, 2740, 2756, 2778, 2818, 2828, 2844, 2850, 2912, 2960, 2992, 3154 |
| §2 Casper | `mynotes.older.txt` / `AICHAT/Notes.txt` | 97, 423–477, 537, 565, 583, 615 / 69, 83 |
| §3 Cmdline | `mynotes.new.txt` | 623–625, 775–795 |
| §4 Services | `mynotes.older.txt` | 1581, 1847, 1879–1903 |
| §5 Resolved | `readme\|12000lines.txt` | as §1 plus 2670, 2716 |
| §6 ALSA | `readme\|12000lines.txt`, `mynotes.new.txt` | 2470, 2576, 2642, 3642–3678 / 149, 679, 737–759 |
| §7 Bait dir | `readme\|12000lines.txt` | 3630–3678 |
| §8 Sysusers | `readme\|12000lines.txt` | 2960 |
| §9 AppArmor | `readme\|12000lines.txt` | 2844, 2850 |
| §10 Cheap wins | `mynotes.new.txt` | 295–337, 561–567, 785, 795 |
| §11 Verify | derived from §1–§10 | n/a |

Cross-references: Reports 22 (pre-overlay breach), 26–33 (systemd / kernel hardening reference), 34 (COW overlay kill), 37 (pre-GRUB VT hijack), 38 (OCR wanker dir), 39 (payback operation).

---

**Status:** Hardening reference, not investigation. File this with reports 26–33 in `reports/hardening/`. When the next batch of screenshots / boots lands, append a §13 on the next "what changed" rather than rewriting this — the cmdline and service list are stable; the rootkit's *new* tricks each cycle should land in a delta section.
