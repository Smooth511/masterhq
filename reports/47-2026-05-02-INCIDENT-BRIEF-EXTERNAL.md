Linux rootkit, ~3 months, ASUS PRIME B460M-A, NVMe. Multiple reinstalls, all reinfected. C3.

CONFIG_XEN_PV_DOM0=y + CONFIG_XEN_PVHVM_GUEST=y in live kernel .config. ACPI persistence. MOK self-signed, re-enrolled after deletion. Pre-GRUB VT on tty7. /cdrom/boot/grub/grub.cfg sources /boot/grub/grub.cfg. plainmount in moddep.lst, OverlayFS lowerdir set before kernel hand-off. /cow/work/upper looted: Casper persistence, credential harvest including same-session passwords, Timeshift intercept. /proc/1860/task/1860/patch_state, VFS + procfs hooks livepatched. PID 1686: ksm_merging_pages + match_state in procfs. PIDs 1686, 1792, 1859, 1860 timerslack_ns EPERM. ISO is a full self-compiling build system, per-component Makefiles, fresh kernel + signatures per deployment, presents as 7.0.0-10-generic. Embedded LLM, output in evidence. tasks.ics dropped to host without connected device. C2 nss.peristor.com, zero hits across all feeds. permissions.sqlite.pdf in rootkit Desktop namespace, SQLite masquerading as PDF, references nss.peristor.com. Active operator, reactive.

Overlaps with Bootkitty (grub_verifiers_open, module_sig_check, version string spoof) and VoidLink (C2-side kernel compilation). Pre-GRUB VT, in-GRUB plainmount, standalone self-compiling ISO, KSM match_state — nothing public. nss.peristor.com unattributed.

github.com/Smooth511/masterhq reports 1–46.
