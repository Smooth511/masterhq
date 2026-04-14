# MigLog.xml Analysis - Windows Install Interception Evidence

**Date:** 2026-03-19  
**Analyst:** ClaudeMKII  
**Source:** User screenshots during Windows install interception investigation  
**File Analyzed:** MigLog.xml (USMT Migration Log)

---

## Screenshots Received

| # | Image ID | Content Summary |
|---|----------|-----------------|
| 1 | e3c6e080 | ShellFolders, Start Menu shortcuts for user "Lloyd" |
| 2 | 4d7a5e05 | More shortcuts, User definition for "Default User" |
| 3 | 02b03e4b | CSIDL and FOLDERID environment mappings |
| 4 | 4aa25da7 | Lloyd's mappings + Downloads folder enumeration |
| 5 | ecfcd578 | Lloyd profile continuation + suspicious second user |

**Status:** 5 of 16 images received. Awaiting remaining 11.

---

## Critical Findings

### 1. Ghost Administrator Account

```xml
<User Valid="YES" Name="" Domain="MINITNS" ID="USER000000000" 
      Admin="false" Selected="true" HasProfile="true" 
      LastAccess="2020/03/18 9:56:16.079" 
      ProfilePath="C:\Users\lloyg" 
      SID="S-1-5-21-...">
  <Groups>
    <Group Name="Administrators"/>
    <Group Name="Users"/>
  </Groups>
</User>
```

**Red flags:**
- Empty `Name=""` attribute
- Profile path typo: `lloyg` instead of `Lloyd`
- Admin group membership despite `Admin="false"` attribute
- Old timestamp (2020) suggests pre-existing hidden account

### 2. Suspicious Files in Downloads

Location: `C:\Users\Lloyd\Downloads\`

| Filename | Concern |
|----------|---------|
| `Defender_Windo_X...45a3-9d0b-r5157Sc3ehk.exe` | Impersonates Windows Defender |
| `6e7ceub2-2201-11f1-01fc-e3f5303bcab.tar.gz` | GUID-named archive |
| `ntgs_github.coe.realiot.com` | Unknown domain reference file |
| `AllEventInfo0721003.evtx` | EVTX file - possible exfil prep |

### 3. Broken Shortcut Targets

Multiple shortcuts have `Target Path="UNKNOWN"`:
- Start Menu shortcuts that should resolve but don't
- Could indicate:
  - Tampered shortcuts
  - Hidden executables
  - Malware cleanup artifacts

### 4. Machine Name Discrepancy

- MigLog shows: `MINITNS`
- Previous investigation referenced: `Mini-Tank-MKII`
- Needs confirmation if same machine or different

---

## User Profiles Identified

| User | Domain | Profile Path | Admin | Notes |
|------|--------|--------------|-------|-------|
| Default User | MINITNS | %DEFAULTUSERPROFILE% | No | Standard template |
| Lloyd | MINITNS | C:\Users\Lloyd | Unknown | Primary user |
| (empty) | MINITNS | C:\Users\lloyg | Yes* | Suspicious typo path |

*Has Administrators group membership

---

## Environment Mappings (Standard)

All standard Windows CSIDL and FOLDERID mappings present:
- AppData (Roaming/Local/LocalLow)
- Program Files (x86/x64)
- VirtualStore compatibility paths
- User shell folders (Documents, Downloads, Pictures, etc.)

**Chocolatey installed:** `%ChocolateyLastPathUpdate%` mapping present

---

## Software Inventory (from shortcuts)

- Visual Studio Code (v1.112.0)
- Git (v2.53.0)
- Node.js (v24.14.0)
- PowerShell ISE
- WinRAR (v7.20.0)
- Firefox
- GitHub Desktop

---

## Next Steps

1. [ ] Receive remaining 11 screenshots
2. [ ] Investigate `lloyg` profile on disk
3. [ ] Analyze `Defender_Windo_X*.exe` if available
4. [ ] Check `ntgs_github.coe.realiot.com` domain
5. [ ] Correlate with EVTX logs
6. [ ] Identify what process created MigLog.xml

---

## Raw Image References

- IMG 1: https://github.com/user-attachments/assets/e3c6e080-28f9-42ef-bbfc-081bb0ea9b49
- IMG 2: https://github.com/user-attachments/assets/4d7a5e05-2f5f-408c-859f-9b89b6f36366
- IMG 3: https://github.com/user-attachments/assets/02b03e4b-aae6-4bc3-8fad-d44bbb878912
- IMG 4: https://github.com/user-attachments/assets/4aa25da7-1b51-412a-b68d-ef71346b1bf8
- IMG 5: https://github.com/user-attachments/assets/ecfcd578-5771-487c-a624-a415cba26dc7
