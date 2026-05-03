#!/usr/bin/env bash
# collect-system-state.sh
# Run as root on the OEM Mint install.
# Output: full system state dump for agent context loading.
# Usage: bash tools/collect-system-state.sh > context/SYSTEM-STATE.txt

set -euo pipefail

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

hr() { echo ""; echo "════════════════════════════════════════════════════════"; echo "  $1"; echo "════════════════════════════════════════════════════════"; }

echo "# SYSTEM STATE DUMP"
echo "# Generated: $TIMESTAMP"
echo "# Machine: $(hostname 2>/dev/null || echo UNKNOWN)"
echo "# Run as: $(whoami) (uid=$(id -u) gid=$(id -g))"
echo ""

hr "CURRENT USER"
id
echo ""
cat /proc/self/status 2>/dev/null | grep -E "^(Name|Uid|Gid|Groups|NSpgid|NStgid):" || true

hr "ALL USERS (/etc/passwd)"
cat /etc/passwd 2>/dev/null || echo "UNREADABLE"

hr "GROUPS (/etc/group)"
cat /etc/group 2>/dev/null || echo "UNREADABLE"

hr "SHADOW (if readable)"
cat /etc/shadow 2>/dev/null || echo "NOT READABLE (expected unless root)"

hr "HOSTNAME / OS RELEASE"
echo "Hostname: $(cat /etc/hostname 2>/dev/null || hostname)"
echo ""
cat /etc/os-release 2>/dev/null || echo "NO OS-RELEASE"

hr "KERNEL / BOOT"
uname -a
echo ""
echo "Cmdline: $(cat /proc/cmdline 2>/dev/null)"
echo ""
echo "Kernel modules loaded:"
lsmod 2>/dev/null | head -60 || echo "lsmod unavailable"

hr "PARTITIONS (lsblk)"
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT,UUID,PARTUUID 2>/dev/null || echo "lsblk unavailable"

hr "PARTITIONS (fdisk)"
fdisk -l 2>/dev/null || echo "fdisk unavailable"

hr "MOUNTS"
mount 2>/dev/null || cat /proc/mounts 2>/dev/null || echo "unavailable"

hr "DISK USAGE"
df -h 2>/dev/null || echo "df unavailable"

hr "FILESYSTEM ROOT (depth 3)"
find / -maxdepth 3 -not -path '*/proc/*' -not -path '*/sys/*' -not -path '*/dev/*' \
    -not -path '*/run/*' -not -path '*/snap/*' 2>/dev/null \
    | sort | head -500 || echo "find unavailable"

hr "/home LAYOUT"
ls -laR /home 2>/dev/null | head -300 || echo "unavailable"

hr "/etc LAYOUT"
ls -la /etc 2>/dev/null || echo "unavailable"

hr "KEY CONFIG FILES"
for f in /etc/fstab /etc/hosts /etc/resolv.conf /etc/nsswitch.conf /etc/sudoers /etc/machine-id; do
    echo ""
    echo "--- $f ---"
    cat "$f" 2>/dev/null || echo "UNREADABLE/MISSING"
done

hr "SUDO CONFIG"
cat /etc/sudoers 2>/dev/null || echo "unreadable"
ls -la /etc/sudoers.d/ 2>/dev/null || true

hr "OEM SPECIFIC"
echo "Checking /home/oem..."
ls -laR /home/oem 2>/dev/null | head -200 || echo "/home/oem does not exist or unreadable"

echo ""
echo "Checking /var/lib/oem* ..."
ls -la /var/lib/oem* 2>/dev/null || echo "nothing"

echo ""
echo "Checking /etc/oem*..."
ls -la /etc/oem* 2>/dev/null || echo "nothing"

echo ""
echo "OEM ubiquity/casper residuals:"
ls -la /cdrom /lib/live /run/live 2>/dev/null || echo "none visible"

hr "PROCESS LIST"
ps auxf 2>/dev/null | head -150 || ps aux 2>/dev/null | head -150 || echo "unavailable"

hr "SYSTEMD SERVICES (active)"
systemctl list-units --type=service --state=active --no-pager 2>/dev/null | head -80 || echo "systemctl unavailable"

hr "NETWORK INTERFACES"
ip addr 2>/dev/null || ifconfig 2>/dev/null || echo "unavailable"

hr "ROUTING TABLE"
ip route 2>/dev/null || route 2>/dev/null || echo "unavailable"

hr "OPEN SOCKETS"
ss -tulnp 2>/dev/null | head -60 || netstat -tulnp 2>/dev/null | head -60 || echo "unavailable"

hr "CRON JOBS"
crontab -l 2>/dev/null || echo "none for current user"
echo ""
ls -la /etc/cron* /var/spool/cron 2>/dev/null || echo "unavailable"

hr "STARTUP / AUTOSTART"
ls -la /etc/init.d/ 2>/dev/null | head -40 || echo "unavailable"
echo ""
ls -la /etc/rc*.d/ 2>/dev/null | head -40 || echo "unavailable"
echo ""
ls -la ~/.config/autostart/ 2>/dev/null || echo "no autostart for current user"
echo ""
ls -la /home/oem/.config/autostart/ 2>/dev/null || echo "no /home/oem autostart"

hr "GRUB CONFIG"
cat /etc/default/grub 2>/dev/null || echo "unavailable"
echo ""
cat /boot/grub/grub.cfg 2>/dev/null | head -80 || echo "unavailable"

hr "RECENT FILE MODIFICATIONS (last 48h)"
find / -maxdepth 5 -not -path '*/proc/*' -not -path '*/sys/*' -not -path '*/dev/*' \
    -newer /tmp -mtime -2 2>/dev/null | sort | head -200 || echo "unavailable"

hr "BASH HISTORY (current user)"
cat ~/.bash_history 2>/dev/null | tail -100 || echo "unavailable"

hr "ROOT BASH HISTORY"
cat /root/.bash_history 2>/dev/null | tail -100 || echo "unavailable or not root"

hr "INTERESTING LOG SNIPPETS"
journalctl -n 100 --no-pager 2>/dev/null || tail -100 /var/log/syslog 2>/dev/null || echo "unavailable"

hr "SETUID/SETGID BINARIES"
find / -maxdepth 6 -not -path '*/proc/*' -not -path '*/sys/*' \
    \( -perm -4000 -o -perm -2000 \) -type f 2>/dev/null | sort || echo "unavailable"

hr "WORLD-WRITABLE DIRECTORIES"
find / -maxdepth 5 -not -path '*/proc/*' -not -path '*/sys/*' \
    -type d -perm -o+w 2>/dev/null | sort | head -50 || echo "unavailable"

echo ""
echo "════════════════════════════════════════════════════════"
echo "  END OF DUMP — $TIMESTAMP"
echo "════════════════════════════════════════════════════════"
