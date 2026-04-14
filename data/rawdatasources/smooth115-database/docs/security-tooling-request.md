# Security Tooling Acquisition Request

> **STATUS: PENDING USER AUTHORIZATION**
> Nothing in this document is live or approved. All download links and commands are staged
> and must not be executed until the owner explicitly authorizes implementation (see
> [Authorization Gate](#authorization-gate) below).

---

## 1. Request Context

The repository owner has requested that the following three Linux (Ubuntu) security tools be
staged for controlled acquisition. Due to network/platform restrictions on the owner's device,
downloads cannot be initiated directly. This document captures the intent, source links, and
command workflows so the owner can review and approve them before anything is actioned.

| Tool | Purpose |
|------|---------|
| **chkrootkit** | Locally checks for signs of a rootkit on the host system |
| **rkhunter** | Rootkit Hunter — scans for rootkits, backdoors, and local exploits |
| **ClamAV** | Open-source antivirus engine for detecting trojans, viruses, malware |

---

## 2. Source Links

### chkrootkit
- **Direct source tarball (requested URL):**
  `ftp://ftp.chkrootkit.org/pub/seg/pac/chkrootkit.tar.gz`
  > ⚠️ FTP transmits data unencrypted. Verify download integrity using the MD5/SHA checksums
  > published on the project home page before use.
- **Project home:** <http://www.chkrootkit.org/>

### rkhunter
- **Official project site:** <https://rkhunter.sourceforge.net/>
- **SourceForge files (all releases):** <https://sourceforge.net/projects/rkhunter/files/>

### ClamAV
- **Official downloads page:** <https://www.clamav.net/downloads>
- **Ubuntu package tracker:** <https://packages.ubuntu.com/source/clamav>

---

## 3. Ubuntu Command Guide

> ⚠️ **Do not run any of the following commands until authorization is given (Section 4).**

### 3.1 chkrootkit

```bash
# Refresh package metadata
sudo apt update

# Install via apt (Ubuntu repositories)
sudo apt install chkrootkit

# Run a scan
sudo chkrootkit

# Verify installed version
chkrootkit -V
```

> *Alternatively, to install from the official source tarball:*
> ```bash
> # Download (once authorized)
> wget ftp://ftp.chkrootkit.org/pub/seg/pac/chkrootkit.tar.gz
> # Verify checksum against value published at http://www.chkrootkit.org/ before proceeding
> tar -xzf chkrootkit.tar.gz
> cd chkrootkit-*/
> make sense
> sudo ./chkrootkit
> ```

---

### 3.2 rkhunter

```bash
# Refresh package metadata
sudo apt update

# Install
sudo apt install rkhunter

# Update rkhunter data files (signatures / known-good hashes)
sudo rkhunter --update

# Set a baseline of file properties
sudo rkhunter --propupd

# Run a full scan
sudo rkhunter --check

# Verify installed version
rkhunter --version
```

---

### 3.3 ClamAV

```bash
# Refresh package metadata
sudo apt update

# Install ClamAV and the daemon
sudo apt install clamav clamav-daemon

# Stop the daemon before manual database update
sudo systemctl stop clamav-freshclam

# Update virus definitions
sudo freshclam

# Restart the daemon
sudo systemctl start clamav-freshclam

# Scan a directory (e.g. home directory)
sudo clamscan -r --bell -i /home

# Check service status
sudo systemctl status clamav-daemon

# Verify installed version
clamscan --version
```

---

## 4. Authorization Gate

**No action is to be taken on any of the above until the repository owner explicitly approves
this pull request and marks the checklist below as complete.**

To authorize:
1. Review Sections 2 and 3 above.
2. Merge this PR to `main`.
3. Tick each item in the Completion Checklist (Section 5) once the corresponding step has been
   carried out on the target system.

---

## 5. Completion Checklist

Mark each item `[x]` after the owner has authorized and the step has been completed:

- [ ] Owner has reviewed and approved this PR
- [ ] PR merged into `main`
- [ ] `chkrootkit` installed and initial scan run
- [ ] `rkhunter` installed, data files updated, and initial scan run
- [ ] `clamav` installed, virus definitions updated, and initial scan run
- [ ] All scan outputs reviewed and any findings addressed
