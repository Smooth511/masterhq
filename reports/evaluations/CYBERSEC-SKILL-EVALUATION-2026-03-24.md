# Claude-Code-CyberSecurity-Skill Evaluation Report
**Date:** 2026-03-24T02:43 UTC  
**Source:** https://github.com/Smooth115/Claude-Code-CyberSecurity-Skill  
**Evaluated by:** ClaudeMKII (MK2_PHANTOM session)

---

## Repository Overview

**15 Claude Code Skills** for cybersecurity, following the SKILL.md format. All Python-based — **no PowerShell scripts**.

### Skill Collection

| # | Skill | Domain | Key Script(s) |
|---|-------|--------|---------------|
| 01 | Recon & OSINT | Reconnaissance | — |
| 02 | Vulnerability Scanner | Assessment | — |
| 03 | Exploit Development | Offensive | — |
| 04 | Reverse Engineering | Analysis | — |
| 05 | Malware Analysis | Threat Analysis | `static_analyzer.py`, `yara_generator.py` |
| 06 | Threat Hunting | Hunting | `ioc_extractor.py`, `mitre_mapper.py` |
| 07 | Incident Response | IR & Forensics | `timeline_builder.py` |
| 08 | Network Security | Network | — |
| 09 | Web Security | Web | — |
| 10 | Cloud Security | Cloud | — |
| 11 | CSOC Automation | SOC Operations | — |
| 12 | Log Analysis & SIEM | Log Analysis | — |
| 13 | Cryptographic Analysis | Cryptography | — |
| 14 | Red Team Operations | Red Team | `engagement_planner.py` |
| 15 | Blue Team Defense | Blue Team | `hardening_checker.py` |

---

## Scripts Evaluated (Most Relevant to Current Investigation)

### 1. `static_analyzer.py` (Malware Analysis)
**Purpose:** Static analysis of suspicious binaries without execution

**Capabilities:**
- Multi-hash calculation (MD5, SHA1, SHA256, SHA512)
- File type identification via magic bytes
- Shannon entropy calculation (packing/encryption detection)
- String extraction and categorization (URLs, IPs, emails, paths, registry, suspicious strings)
- Packer detection (UPX, ASPack, Themida, VMProtect, etc.)
- IOC generation

**Use case for us:** Analyze extracted suspicious binaries from the Windows cleanup

### 2. `ioc_extractor.py` (Threat Hunting)
**Purpose:** Extract IOCs from text, reports, and logs

**Capabilities:**
- Regex-based extraction: IPv4/IPv6, domains, URLs, emails
- Hash extraction: MD5, SHA1, SHA256, SHA512
- CVE and MITRE technique ID extraction
- Registry keys, file paths (Windows/Unix)
- Bitcoin addresses, mutex names
- Defanging for safe sharing
- Output formats: JSON, CSV, STIX 2.1

**Use case for us:** Pull indicators from collected logs/reports

### 3. `timeline_builder.py` (Incident Response)
**Purpose:** Forensic timeline from multiple log sources

**Capabilities:**
- Parses multiple timestamp formats (ISO 8601, syslog, Apache, Windows Event, epoch)
- Severity classification (CRITICAL/HIGH/MEDIUM/LOW/INFO)
- Time range filtering
- Export to CSV, JSON, HTML
- Handles directory recursion

**Use case for us:** Correlate multi-source forensic data from evidence collection

### 4. `hardening_checker.py` (Blue Team)
**Purpose:** Linux hardening audit (CIS-style)

**Capabilities:**
- SSH config validation
- Firewall status check
- SUID binary enumeration
- Unnecessary service detection
- Audit daemon verification

**Note:** Linux-focused, limited Windows applicability

---

## Missing Capabilities

**NOT in this repo:**
- ❌ PowerShell scripts
- ❌ Windows-specific tooling
- ❌ EVTX parsing (we already have this locally in Claude-MKII)
- ❌ Registry hive analysis
- ❌ MFT/NTFS analysis
- ❌ Memory dump analysis scripts

**We already have locally:**
- `tools/parse_evtx.py` — Windows Event Log parsing
- `tools/safe_read.py` — Safe file reading with detection logging

---

## Integration Decision

### Per Repo Policy
**No external access to Claude-MKII repo.** Any integration must be:
1. Manual import to internal sub-repo for verification first, OR
2. Run manually outside the repo

### Recommendation
- **Copy scripts locally** if needed for analysis
- **Reference externally** for methodology/procedures
- Scripts are standalone Python with minimal dependencies (`pyyaml`, `jinja2`, `pandas`)

---

## Scripts Worth Importing (If Approved)

| Script | Why | Dependencies |
|--------|-----|--------------|
| `static_analyzer.py` | Binary analysis for extracted artifacts | None (stdlib only) |
| `ioc_extractor.py` | IOC extraction from any text/logs | None (stdlib only) |
| `mitre_mapper.py` | ATT&CK technique mapping | `pyyaml`, `requests` |

---

## Red Team Skill Notes

The **14-red-team-ops** skill documents persistence mechanisms that may be relevant for understanding what we're fighting:

**Persistence categories mentioned:**
1. Registry run keys and startup folder
2. Scheduled tasks and services
3. DLL hijacking and COM objects
4. WMI event subscriptions
5. Golden/Silver tickets (AD)
6. DACL/SACL manipulation
7. Web shells
8. Firmware/UEFI-level (advanced)

**Attacker countermeasure context:** User reports system crashes when approaching critical persistence during cleanup. Kali boot bypasses crash triggers.

---

## Next Steps (Pending User Direction)

- [ ] User decides: copy scripts locally vs reference-only
- [ ] If copying: import to `tools/external/` with source attribution
- [ ] Continue cleanup from Kali boot to avoid crash triggers
- [ ] Use `ioc_extractor.py` on collected evidence once imported

---

*Report generated by ClaudeMKII. No code changes made — evaluation only.*
