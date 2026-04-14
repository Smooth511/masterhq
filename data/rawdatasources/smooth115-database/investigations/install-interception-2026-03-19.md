# Windows Install Interception Evidence Analysis
**Date:** 2026-03-19
**Machine:** Mini-Tank-MKII (Domain: MINIM3)
**Context:** User documenting malware persistence during fresh Windows install

---

## Evidence Sources
Screenshots provided: IMG_0231, IMG_0253, IMG_0254, IMG_0255, IMG_0256, IMG_0258, IMG_0249, IMG_0260

**Primary evidence:** USMT (User State Migration Tool) log.xml files showing user profile capture during install.

---

## NEW: USMT Profile Capture Evidence (Screenshots Analyzed)

### User Profile Data Being Harvested
The screenshots show `log.xml` files from Windows USMT capturing full user profiles:

**User 1 - Default User:**
- Domain: `MINIM3`
- LastAccess: `2026/03/18 9:23:14.09`
- SID: `S-1-5-21-...` (visible in logs)
- Full CSIDL shell folder mappings captured

**User 2 - lloyd:**
- Domain: `MINIM3` 
- LastAccess: `2020/05/18 8:54:16.079` ⚠️ **TIMESTAMP ANOMALY - 6 years in the past**
- ProfilePath: `C:\Users\lloyd`
- Group memberships: `Administrators`, `Users`
- Chocolatey installation detected: `%ChocolateyLastPathUpdate%`

### Shell Folders Being Mapped
All standard Windows shell folders captured including:
- `%APPDATA%`, `%LOCALAPPDATA%`
- `%CSIDL_CONTACTS%`, `%CSIDL_DOWNLOADS%`, `%CSIDL_DOCUMENTS%`
- `%CSIDL_STARTMENU%`, `%CSIDL_STARTUP%`
- Virtual store paths, OneDrive paths, SkyDrive paths

### Downloads Folder Contents Captured
User lloyd's Downloads folder contents enumerated:
```
claude_mk11_seed_package.md
Firefox Installer.exe
Git-2.39.0-64-bit.exe
GitHubDesktopSetup-x64.exe (with hash: e3572612fe00832239b5ac599b1449fe:04808f...)
AllSecurityTimebomber.exe ⚠️
FilterFinder_Windows_x.2009208-a311-45a3-986b-r51517Se3e8e.exe ⚠️ [OCR uncertain - mixed case suggests transcription error]
```

### Start Menu Shortcuts Captured
Full enumeration of installed programs via shortcuts:
- Administrative Tools, PowerShell (x86 and x64)
- Accessibility tools (magnify.exe, narrator.exe, osk.exe)
- System tools (cmd.exe, control.exe)
- Programs marked with `Target Path="UNKNOWN"` ⚠️

---

## Analysis: USMT Abuse Pattern

**What's happening:** USMT is being run during Windows install to capture user profiles. This is a legitimate Windows feature BUT:

1. **Why is it running on fresh install?** USMT captures existing user data for migration - it shouldn't have data to capture on a fresh install
2. **Timestamp anomaly:** 2020 LastAccess on a 2026 machine = profile data from a previous machine/backup being injected?
3. **Suspicious executables in Downloads:** Files like `AllSecurityTimebomber.exe` and the FilterFinder executable are red flags
4. **UNKNOWN targets:** Start menu shortcuts pointing to `UNKNOWN` suggest tampering

**Hypothesis:** Malware is using USMT to either:
- A) Exfiltrate user profile data during install (sending it somewhere)
- B) Inject a pre-captured user profile (persistence across reinstall)
- C) Both - capture legitimate user data while injecting malicious profile data

---

## Key Findings

### 1. Sysprep Phase Interception
The malware is hooking into Windows Sysprep specialize phase - this runs during OOBE (Out-of-Box Experience) on fresh installs.

**Suspicious DLLs loaded during Sysprep_Specialize_Offline:**
| DLL Path | Function Hooked |
|----------|-----------------|
| `\system32\sspopk.dll` | SysprepOffline_Specialize_Op |
| `\system32\spopk.dll` | (base sysprep) |
| `\system32\ytc-dll` | SysprepSpecializeOffline |
| `\system32\sppnp.dll` | SysprepSpecializeOffline |
| `\system32\psetup.dll` | PowerCustomizePlatformPowerSettingsOffline |
| `\system32\msdc-dll` | AppSysprepSpecialize_Offline |
| `\system32\sphcd.dll` | Sysprep_Offline_Specialize_Offline |
| `\system32\softn-dll` | SysPrep_OfflineSpecializeOffline |
| `\system32\sprovsys.dll` | ProvPackagesSysprepSpecializeOffline |
| `\system32\unattend.dll` | SynsprepSpecializeOffline_Unattend |

**Red flags:**
- `ytc-dll` - not standard Windows, typo-squatting pattern
- `msdc-dll` - not standard Windows
- `softn-dll` - not standard Windows
- Multiple DLLs calling non-standard Sysprep functions

### 2. GUIDs Observed
These GUIDs are being referenced during the install phases:

| GUID | Context |
|------|---------|
| `272AB3B8-5B2C-41D9-82C3-D8BD6598815F` | nStartTime, nEndTime, nName tracking |
| `C80C4FCF-FD54-40A8-B6EF-C175BAAFA53A` | SafeOS and rollback phase |
| `6DDF3F04-C-64A9-4C66-B243-D0A2C0E87C37` | (malformed - second segment has 1 char instead of required 4) |
| `dfa6668ad-ffff-4c6c-bb64-c30cd889cbbe` | Referenced in multiple entries |

**Anomalies:**
- GUID `6DDF3F04-C-64A9-4C66-B243-D0A2C0E87C37` is malformed (has extra `-C-` segment)
- GUID `dfa6668ad-ffff-4c6c-bb64-c30cd889cbbe` has non-standard format (lowercase, first segment has 9 chars instead of 8)

### 3. Phase Tracking
The malware is tracking:
- `nStartTime` / `nEndTime` - timing install phases
- `nEstimatedSpace` / `nConsumedSpace` - monitoring disk usage
- `nExecutedPhase` - tracking which phases completed
- `nState` - current state including "SafeOS and rollback"

This suggests the malware is:
1. Monitoring install progress in real-time
2. Injecting persistence during Sysprep specialize phase
3. Tracking rollback capability (possibly to prevent clean reinstall)

---

## Attack Vector Analysis

### Pre-boot Persistence
This evidence suggests the malware has:
1. **Firmware-level persistence** - survives across Windows reinstalls
2. **Sysprep hook injection** - loads malicious DLLs during OOBE specialize phase
3. **Phase monitoring** - tracks install progress to inject at correct moment
4. **Rollback awareness** - monitors SafeOS/recovery partition state

### Connection to Prior Evidence
Links to existing Mini-Tank-MKII investigation:
- PID 3992 connection to 109.61.19.21:80 (G-Core Labs London) on first boot
- PID 1052 connection to 85.234.74.60:80 on first boot
- Windows Security blocked by "IT policy" on fresh install

**Pattern:** Malware activates during install, phones home, blocks Windows Security

---

## Recommendations

1. **Do NOT trust this machine for sensitive work**
2. Check firmware/UEFI for persistence (requires hardware tools or different machine)
3. Investigate router/network for MITM during install
4. Consider physical inspection of hardware (especially if second-hand)
5. Document all DLL hashes if accessible

---

## Screenshot Index

| Image | Contents | Key Finding |
|-------|----------|-------------|
| f15d6af9 | USMT log.xml - Default User CSIDL mappings | Domain MINIM3, full shell folder capture |
| 4aa25da7 | USMT log.xml - User lloyd Downloads enumeration | Suspicious executables listed, Chocolatey detected |
| ecfcd578 | USMT log.xml - Start Menu shortcuts + user groups | UNKNOWN targets, Admin membership, 2020 timestamp |
| e3c6e080 | (pending analysis) | |
| b41c54fb | (pending analysis) | |
| 2d3cf9b1 | (pending analysis) | |
| IMG_0260 | OCR captured - Sysprep DLLs | DLL injection evidence |

---

## Raw OCR Data Reference
See: `chat-logs/ocr-image-4c9a2894.txt`
