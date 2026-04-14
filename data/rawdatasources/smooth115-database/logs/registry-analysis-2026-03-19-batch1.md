# Registry/Policy Evidence Analysis - Batch 1
**Date:** 2026-03-19 02:06 UTC  
**Source:** Windows Install Interception Investigation  
**Images Analyzed:** 4 of 16 (12 more pending)

---

## Executive Summary

These screenshots show XML exports of Windows shell folder configurations and user profile data, likely from a RegLog or similar registry export tool. Key findings include suspicious entries with `UNKNOWN` target paths and evidence of profile manipulation during Windows installation.

---

## Image 1 Analysis (IMG_0253)

### File Type
XML registry/shell folder export (appears to be from a migration or setup log)

### Key Entries Observed

#### User Profile - Suspicious
```
User Valid="YES" Name="Default User" Domain="MINITMS" ID="USER000000001" 
Admin="False" Selected="True" HasProfile="True" 
LastAccess="2026/03/18 9:23:14.097"
ProfilePath="%DEFAULTUSERPROFILES%" 
SID="-1-0-0"
```
**⚠️ FLAGS:**
- SID "-1-0-0" is NOT a valid Windows SID format
- %DEFAULTUSERPROFILES% variable is non-standard
- Domain "MINITMS" matches machine name from prior investigation

#### Shell Folders Mapped
- APPDATA, COOKIES, CONTACTS, DESKTOP, DOWNLOADS, FAVORITES
- Standard CSIDL redirections present
- Start Menu shortcuts for:
  - Git GUI, Git Release Notes
  - Maintenance, Node.js (cmd, documentation, website)
  - PowerShell ISE (x86), WinRAR
  - msiexec.exe referenced (Windows Installer)

---

## Image 2 Analysis (IMG_0254)

### Continuation of Shell Folder Mappings

#### FOLDERID Entries (Modern Windows API)
```
FOLDERID_Downloads -> C:\Users\Default\Downloads
FOLDERID_Contacts -> C:\Users\Default\Contacts  
FOLDERID_GameTasks -> C:\Users\Default\AppData\Local\Microsoft\Windows\GameExplorer
FOLDERID_Libraries -> C:\Users\Default\AppData\Roaming\Microsoft\Windows\Libraries
FOLDERID_LocalAppDataLow -> C:\Users\Default\AppData\LocalLow
FOLDERID_OriginalImages -> C:\Users\Default\AppData\Local\Microsoft\Windows Photo Gallery\Original Images
FOLDERID_SkyDriveCameraRoll -> C:\Users\Default\SkyDrive\Pictures\Camera Roll
```

#### VirtualStore Paths
```
MCSIDL_VIRTUALSTORE_COMMONPROGRAMFILES -> VirtualStore\Program Files\Common Files
MCSIDL_VIRTUALSTORE_PROGRAMFILES(X86) -> VirtualStore\Program Files (x86)\Common Files
```
VirtualStore presence indicates UAC redirection active.

#### ShellFolder ObjectCounts
Multiple entries with `<Recap ObjectCount="1"/>` through `<Recap ObjectCount="4"/>`
- Downloads, Desktop, Favorites, Music, Pictures, Videos, Documents all present
- CSIDL_PERSONAL includes My Music/, My Pictures/, My Videos/ subdirectories

---

## Image 3 Analysis (User: Lloyd)

### Profile Switch Observed
Now showing user "Lloyd" instead of "Default User":
```
C:\Users\Lloyd\...
```

### ⚠️ SUSPICIOUS DOWNLOADS FOLDER CONTENTS

Files visible in Lloyd's Downloads:
```
6eceub82-2201-11f1-011c-e3f5100bcab.tar.gz    # UUID-format filename - suspicious
AI powerlyzer.exe                              # Unknown executable
AllSecurityTimebroker.exe                      # Suspicious name pattern
AllEvents1n072180A.evtx                        # Event log export  
FilterFolder_Window_420092b8-a311-45a3-98b5-f5157563e8c.exe   # UUID in filename
claude_mkII_seed_package.md                    # Our file (expected)
GettingStarted.md
Firefox Installer.exe                          # Standard
Git-2.5.0-64-bit.exe                          # Standard
GitHubDesktopSetup-x64.exe                    # Hash: e9577621efeb0832396f5ac5990144f...
mtps__github.com_CodeFile.exe                 # Suspicious - GitHub domain in exe name
```

**⚠️ HIGH PRIORITY FILES FOR ANALYSIS:**
1. `AllSecurityTimebroker.exe` - name suggests security/timing manipulation
2. `FilterFolder_Window_*.exe` - UUID-pattern filename common in malware
3. `mtps__github.com_CodeFile.exe` - unusual naming with domain reference
4. `AI powerlyzer.exe` - unknown purpose
5. `6eceub82-2201-11f1-011c-e3f5100bcab.tar.gz` - UUID archive

### Same FOLDERID Structure
- OneDrive paths present: `%OneDrive%`, `%OneDriveConsumer%`
- XPath reference: `C:\Users\Lloyd\AppData\Local\Programs\Microsoft VS Code\bin\...`

---

## Image 4 Analysis (Start Menu + Profile Details)

### CSIDL_STARTMENU Structure

#### Standard Accessibility Tools
```
magnify.exe     ProductVersion="10.0.22621.5547"
narrator.exe    ProductVersion="10.0.22621.4838"  
osk.exe         ProductVersion="10.0.22621.5262"
UtilMan.exe     (Utility Manager)
AtBroker.exe    (Assistive Technology)
```

#### ⚠️ CRITICAL - UNKNOWN TARGET SHORTCUTS
Multiple entries with:
```
<Shortcut Path="C:\Users\Default\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\[name].lnk">
    <Target Path="UNKNOWN"/>
</Shortcut>
```

**Shortcuts with UNKNOWN targets:**
- `Programs\Desktop.lnk` -> UNKNOWN
- `Programs\System Tools\Desktop.lnk` -> UNKNOWN  
- `Programs\System Tools\Run.lnk` -> UNKNOWN
- `System Tools\Control Panel.lnk` -> UNKNOWN (noted after cmd.exe entry)

**This is highly suspicious** - legitimate shortcuts should always resolve to valid targets. UNKNOWN targets suggest:
- Shortcuts created before target binaries were staged
- Intentionally broken shortcuts as misdirection
- Malware injection points waiting for payload

### User Profile Details
```
User Valid="YES" Name="" Domain="MINITMS" ID="USER000000000" 
Admin="False" Selected="True" HasProfile="True"
LastAccess="2026/03/18 8:54:16.079"
ProfilePath="C:\Users\Lloyd"
SID="1-5-21-778131152-3653532558-346472719-1001"
```

**⚠️ FLAGS:**
- `Name=""` - EMPTY username in profile (ID is USER000000000)
- The SID format looks more valid: `1-5-21-...`
- Groups membership: Administrators, Users
- ChocolateyLastPathUpdate present - indicates Chocolatey package manager installed

### Environment Mappings
- APPDATA, CSIDL paths continue
- NCSIDL_BURNING_AREA -> `C:\Users\Lloyd\AppData\Local\Microsoft\Windows\MasteredBurningDisc_Burning`

---

## Pattern Analysis

### Tracer UIDs Status
Looking for UIDs 33554432, 50331648, 51150848:
- **NOT FOUND** in this batch
- These may appear in network/policy entries (pending images)

### OneSettings Queries
- **NOT FOUND** in this batch
- Expected in policy/telemetry sections

### Network Profile Manipulation
- Shell folder paths show standard user profile structure
- Domain "MINITMS" consistent across entries
- Multiple profile configurations suggest profile injection during setup

### Suspicious Process Indicators
From Downloads folder:
1. `AllSecurityTimebroker.exe`
2. `FilterFolder_Window_*.exe`
3. `mtps__github.com_CodeFile.exe`
4. `AI powerlyzer.exe`

### C2 Addresses
- **NOT FOUND** in this batch
- May appear in network connection logs

### Policy Entries
- Shell folder redirections documented
- UAC VirtualStore active
- No Group Policy entries visible yet

### Registry Manipulation Evidence
- Non-standard SID "-1-0-0" for Default User
- Empty username with valid profile path
- UNKNOWN target shortcuts (persistence mechanism indicators)

---

## Risk Assessment

| Finding | Severity | Priority |
|---------|----------|----------|
| UNKNOWN target shortcuts | HIGH | Investigate immediately |
| Invalid SID "-1-0-0" | HIGH | Profile manipulation |
| Empty username in USER000000000 | MEDIUM | Enumeration anomaly |
| Suspicious Downloads executables | HIGH | Analyze externally |
| Domain "MINITMS" consistency | INFO | Tracking marker |

---

## Next Steps

1. **Pending:** 12 more images to analyze
2. **Need:** Network profile registry entries 
3. **Need:** Policy/GPO screenshots
4. **Action:** Extract and analyze suspicious executables from Downloads
5. **Action:** Cross-reference SIDs with known malware patterns

---

## Raw Indicators of Compromise (IOCs)

### Files
```
AllSecurityTimebroker.exe
FilterFolder_Window_420092b8-a311-45a3-98b5-f5157563e8c.exe
mtps__github.com_CodeFile.exe
AI powerlyzer.exe
6eceub82-2201-11f1-011c-e3f5100bcab.tar.gz
```

### Registry Anomalies
```
SID: -1-0-0 (invalid format)
Profile: USER000000001 with %DEFAULTUSERPROFILES%
Profile: USER000000000 with empty Name field
Target Path: UNKNOWN (multiple Start Menu shortcuts)
```

### Machine Identifiers
```
Domain: MINITMS
ProfilePath: C:\Users\Lloyd
```

---

*Analysis by ClaudeMKII - Batch 1 of 4*  
*Awaiting remaining 12 images for complete assessment*
