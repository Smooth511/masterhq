# Malware Evidence Analysis Report
**Date:** 2026-03-19  
**Analyst:** ClaudeMKII  
**Context:** Windows install interception malware persistence documentation  
**Source:** 9 screenshots from MigLog.xml and related Windows migration/profile data

---

## Executive Summary

Analysis of Windows Migration Log (MigLog.xml) screenshots reveals evidence of:
1. **Pre-configured user profiles** with suspicious file artifacts in Downloads
2. **Unknown target shortcuts** indicating potential hollowed or hijacked Start Menu entries
3. **Suspicious executables** with GUID-named and anomalous naming patterns
4. **Certutil abuse indicators** - commonly used for LOLBin attacks
5. **Multiple user profile contexts** switching between Default, Lloyd, and MINIM domains

---

## CRITICAL FINDINGS

### 🔴 HIGH SEVERITY - Suspicious Executables

| Filename | Location | Risk Assessment |
|----------|----------|-----------------|
| `FilterFinder_Windows_82089926-8311-45a3-98b5-e51517Sc3c8c.exe` | Lloyd\Downloads | GUID-named exe - likely dropper or beacon |
| `mtps_github.coe.cooliot.exe` | Lloyd\Downloads | Suspicious domain in filename - potential C2 indicator |
| `Certutil.exe.lnk` | Lloyd\Downloads | LOLBin abuse vector - used for download/decode operations |
| `6efeeb82-2261-11f1-01fc-e3f5103bcab.tar.gz` | Lloyd\Downloads | GUID-named archive - potential payload container |

### 🔴 HIGH SEVERITY - Unknown Target Shortcuts

Multiple Start Menu shortcuts have `Target Path="UNKNOWN"` which indicates:
- Shortcuts pointing to non-existent or hidden executables
- Potential placeholder for malware to fill in later
- Evidence of tampered migration data

**Affected entries:**
- Desktop.lnk → UNKNOWN
- File Explorer.lnk → UNKNOWN  
- System Tools\Run.lnk → UNKNOWN
- System Tools\Desktop.lnk → UNKNOWN

### 🟠 MEDIUM SEVERITY - Anomalous Values

| Field | Value | Concern |
|-------|-------|---------|
| ChocolateyLastPathUpdate | `1341820034064DMNC` | Non-standard format - should be timestamp |
| User SID | `S-1-5-21-770333532-365533153B-34647127-1001` | Contains hex 'B' in decimal SID segment |
| LastAccess timestamps | 2026/03/18 | Future-dated (if before this date) or indicates system time manipulation |

---

## USER PROFILE ANALYSIS

### Profile 1: Default User Template
- **Domain:** MINITMS
- **User ID:** USER000000001
- **SID:** S-1-5-0 (Nobody/Null SID - unusual for profile)
- **Profile Path:** %DEFAULTUSERPROFILES%
- **Last Access:** 2026/03/18 09:33:14.097

### Profile 2: Lloyd User (Primary Target)
- **Domain:** MINIM3
- **User ID:** USER0000000000
- **SID:** S-1-5-21-770333532-365533153B-34647127-1001
- **Profile Path:** C:\Users\Lloyd
- **Last Access:** 2026/03/18 08:54:16.079
- **Groups:** Administrators, Users

---

## SOFTWARE INVENTORY (From Shortcuts)

| Software | Version | Publisher | Notes |
|----------|---------|-----------|-------|
| Windows Installer (msiexec) | 5.0.22621.3880 | Microsoft | Standard |
| PowerShell | 10.0.22621.1 | Microsoft | Standard |
| PowerShell ISE | 10.0.22621.1 | Microsoft | Standard |
| WinRAR | 7.20.0 | Alexander Roshal | Standard |
| Git | 2.53.0 | The Git Development Community | Standard |
| Node.js | 24.14.0 | Node.js | Installed |
| Visual Studio Code | 1.112.0 | Microsoft | Installed |
| OneDrive | 26.032.0217.0003 | Microsoft | Installed |

---

## SHELL FOLDER MAPPING ANALYSIS

Standard CSIDL mappings present with no obvious hijacking in visible folders:
- APPDATA, LOCAL_APPDATA, COOKIES, DESKTOP, DOCUMENTS
- DOWNLOADS, FAVORITES, HISTORY, MUSIC, PICTURES, VIDEOS
- STARTMENU, STARTUP, TEMPLATES, NETHOOD, PRINTHOOD
- VirtualStore paths for Program Files redirection

**Potential Concern:** VirtualStore mappings could hide malware in:
- `%LOCALAPPDATA%\VirtualStore\Program Files\`
- `%LOCALAPPDATA%\VirtualStore\Program Files (x86)\`

---

## EVTX FILES FOUND

The following Windows Event Log files were found in Lloyd's Downloads:
1. `AI_hourly_save.evtx`
2. `AllEventsSinceAM721002.evtx`
3. `AllSecurityTimeexcept.evtx`

**Recommendation:** Parse these with `tools/parse_evtx.py` for timeline analysis.

---

## IMAGES NOT ANALYZED (6-9)

Images 6, 7, 8, and 9 could not be viewed due to platform limitations. User should provide key text from:
- Any IP addresses or URLs
- Tracer UIDs (33554432, 50331648, 51150848)
- OneSettings queries
- Network profile GUIDs
- Registry Run/RunOnce keys
- Service entries

---

## INDICATORS OF COMPROMISE (IOCs)

### File-based IOCs
```
FilterFinder_Windows_82089926-8311-45a3-98b5-e51517Sc3c8c.exe
mtps_github.coe.cooliot.exe
6efeeb82-2261-11f1-01fc-e3f5103bcab.tar.gz
Certutil.exe.lnk
```

### Domain/URL IOCs
```
cooliot.exe (embedded in filename - investigate cooliot domain)
coe.cooliot (potential C2 subdomain pattern)
```

### Registry/Path IOCs
```
Target Path="UNKNOWN" (hollowed shortcuts)
ChocolateyLastPathUpdate=1341820034064DMNC (anomalous value)
```

### User/Machine Context
```
Domain: MINITMS, MINIM3
Username: Lloyd
SID: S-1-5-21-770333532-365533153B-34647127-1001
```

---

## RECOMMENDATIONS

1. **Immediate:** Quarantine/image the machine before further use
2. **Parse EVTX files** in Downloads folder for execution timeline
3. **Submit suspicious exes** to sandbox (VirusTotal, Any.Run, Hybrid Analysis)
4. **Check cooliot domain** for known C2 infrastructure
5. **Investigate Unknown target shortcuts** - determine what was supposed to be there
6. **Analyze the GUID-named tar.gz** for payload contents
7. **Check Certutil usage** in event logs for download/decode commands

---

## RAW OBSERVATIONS FROM IMAGES

### Image 1: Start Menu Shortcuts + Default User Profile
- Standard Windows shortcuts for Git, Node.js, PowerShell, WinRAR
- Default user template configuration
- Migration log format (MigLog.xml)

### Image 2: Extended CSIDL Mappings
- Additional folder redirections
- VirtualStore paths
- Shell folder definitions

### Image 3: Lloyd User Downloads (CRITICAL)
- Suspicious executables in Downloads
- EVTX files indicating prior investigation/collection
- GUID-named archives

### Image 4: Lloyd Profile + MINIM3 Domain
- User in Administrators group
- Multiple UNKNOWN target shortcuts
- Anomalous Chocolatey path value

### Image 5: Extended Start Menu Analysis
- Continuation of shortcut mappings
- VS Code, PowerShell, WinRAR entries
- System Tools folder shortcuts

### Images 6-9: NOT ANALYZED
- Platform limit reached
- Await user description of contents

---

*Report generated by ClaudeMKII malware analysis module*
