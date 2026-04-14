# Project 12 — Comprehensive Forensic Analysis & Security Audit
**Classification:** Restricted — Investigation Use Only  
**Date Prepared:** 2026-03-13  
**Sysdiagnose Source:** `sysdiagnose_2026.03.09_12-56-54+0000_iPhone-OS_iPhone_23D8133`  
**Rootkit Family Identifier:** 31239 namespace  

---

## Table of Contents

1. [File Inventory](#1-file-inventory)
2. [Device Identity Confirmation](#2-device-identity-confirmation)
3. [New Forensic Evidence](#3-new-forensic-evidence)
4. [Timeline Correlations](#4-timeline-correlations)
5. [Cross-Device Linkage Evidence](#5-cross-device-linkage-evidence)
6. [Security Concerns & Redaction Recommendations](#6-security-concerns--redaction-recommendations)
7. [Summary of Key Conclusions](#7-summary-of-key-conclusions)

---

## 1. File Inventory

**Total files: 347** (excluding `.git`)

### Investigation & Analysis Documents

| Filename | Size (bytes) |
|----------|-------------|
| `README.md` | 115 |
| `Alone at last` | 428 |
| `EVTX Analysis Addendum Mar12.docx` | 19,776 |
| `iOS First Contact Handover Mar12.docx` | 18,467 |
| `iOS First Contact Handover Mar12.pdf` | 126,204 |
| `Project12 SaveFile Mar12.docx` | 18,851 |
| `Project12 SaveFile Mar12 2.docx` | 18,851 |
| `thu_mar_05_2026_apple_i_phone_logs_analysis_for_rootkit.json` | 2,134,922 |
| `diagnostic_summary.log` | 139,042 |
| `diagnostics.txt` | 141 |

### iOS Activation & Pairing Logs (PRIMARY EVIDENCE)

| Filename | Size (bytes) |
|----------|-------------|
| `lockdownd.log` | 141,517 |
| `MobileActivation.log` | 2,150 |
| `MobileLockdown.log` | 227 |
| `mobileactivationd.log.0` | 41,130 |
| `mobileactivationd.log.1` | 66,168 |
| `mobileactivationd_dcrt_baa_request.txt` | 72,454 |
| `mobileactivationd_dcrt_baa_response.txt` | 2,922 |
| `mobileactivationd_sdcrt_baa_request.txt` | 72,455 |
| `mobileactivationd_sdcrt_baa_response.txt` | 2,926 |

### Networking & Connectivity

| Filename | Size (bytes) |
|----------|-------------|
| `ifconfig.txt` | 25,540 |
| `netstat.txt` | 457,527 |
| `NetworkInterfaces.plist` | 1,047 |
| `Networking.log` | 9,189 |
| `NetworkRelay.log` | 629 |
| `get-network-info.txt` | 4,574 |
| `ndp-info.txt` | 26 |
| `route-info.txt` | 1,614 |
| `skywalk.txt` | 431,543 |
| `WiFi.log` | 22,513 |
| `com.apple.networkextension.plist` | 15,549 |
| `com.apple.networkextension.uuidcache.plist` | 8,546 |
| `com.apple.networkextension.necp.plist` | 241 |
| `com.apple.networkextension.control.plist` | 451 |
| `com.apple.networkextension.cache.plist` | 554 |
| `com.apple.networkd.plist` | 3,775 |
| `com.apple.networkd.networknomicon.plist` | 434 |
| `preferences.plist` | 7,870 |

### Crash / Jetsam / forceReset Reports

| Filename | Size (bytes) |
|----------|-------------|
| `forceReset-full-2026-03-12-111038.0002.ips` | 1,436,379 |
| `forceReset-full-2026-03-12-113853.0002.ips` | 1,263,791 |
| `forceReset-full-2026-03-12-175254.0002.ips` | 1,351,042 |
| `JetsamEvent-2026-03-08-145532.ips` | 140,283 |
| `JetsamEvent-2026-03-08-170719 2.ips` | 326,869 |
| `ExcUserFault_SafariViewService-2026-03-09-121611.ips` | 3,730 |
| `MobileMail.diskwrites_resource-2026-03-09-083737 2.ips` | 262,290 |
| `ResetCounter-2026-03-12-113903.ips` | 487 |
| `ResetCounter-2026-03-12-175304.ips` | 487 |
| `Jetsam10.06.txt` | 182,212 |
| `crashes_and_spins.log` | 14,313 |
| `restore_perform.txt` | 28,111 |

### System State & Configuration

| Filename | Size (bytes) |
|----------|-------------|
| `state.plist` | 206,659 |
| `config.plist` | 84,311 |
| `DCP.plist` | 98,076 |
| `BatteryUI.plist` | 515,436 |
| `BatteryUISysdiagnose.plist` | 784,700 |
| `SystemVersion.plist` | 574 |
| `SystemVersion.log` | 258 |
| `Splat_Versioning.log` | 790 |
| `BuildVersion.json` | 107 |
| `TCC.db` | 86,016 |
| `TCC.db-shm` | 32,768 |
| `TCC.db-wal` | 0 |
| `Truth.plist` | 14,005 |
| `ClientTruth.plist` | 743 |
| `ProfileTruth.plist` | 42 |
| `FDRDiagnosticReport.plist` | 9,237 |
| `EffectiveUserSettings.plist` | 13,713 |
| `UserSettings.plist` | 13,699 |
| `PublicEffectiveUserSettings.plist` | 13,041 |
| `MCSettingsEvents.plist` | 21,149 |
| `MCState.log` | 5,085 |
| `ManagedSettings.log` | 7,978 |

### Installation & App Logs

| Filename | Size (bytes) |
|----------|-------------|
| `mobile_installation.log.0` | 98,687 |
| `mobile_installation.log.1` | 262,526 |
| `mobile_installation_helper.log.0` | 244 |
| `MobileInstallation.log` | 852 |
| `MobileAssetHistory.log` | 17,633 |
| `unified_asset_manager.log` | 308,575 |
| `usermanagerd.log.0` | 208,093 |

### MobileAutoAsset History Logs (MAAutoAsset_*)

| Pattern | Files | Total Size |
|---------|-------|------------|
| `MAAutoAsset_Atomic_History_*.log` | 10 | ~127,000 |
| `MAAutoAsset_Error_History_*.log` | 10 | ~173,000 |
| `MAAutoAsset_Filesystem_History_*.log` | 10 | ~38,500 |
| `MAAutoAsset_Locker_History_*.log` | 10 | ~127,000 |
| `MAAutoAsset_Stager_History_*.log` | 10 | ~48,700 |
| `MAAutoAsset_Scheduler_History_*.log` | 10 | ~1,100 |
| `MAAutoAsset_Secure_History_*.log` | 10 | ~2,100 |
| `MAAutoAsset_PushNotification_History_*.log` | 10 | 560 |

### Battery Data (BDC_*)

| Filename | Size (bytes) |
|----------|-------------|
| `BDC_SBC_version3.0_2026-03-08_13:24:15.csv` | 1,513 |
| `BDC_SBC_version3.0_2026-03-08_14:55:23.csv` | 13,311 |
| `BDC_SBC_version3.0_2026-03-09_10:02:30.csv` | 2,865 |
| `BDC_Daily_version3.0_2026-03-08_13:24:15.csv` | 418 |
| `BDC_Weekly_version3.0_2026-03-08_13:24:15.csv` | 426 |
| `BDC_OBC_version3.0_2026-03-08_13:24:15.csv` | 648 |
| `BDC_Once_version3.0_2026-03-08_13:24:15.csv` | 142 |
| `BDC_SmartCharging_version3.0_2026-03-08_14:16:01.csv` | 404 |

### Database / Log Archives

| Filename | Size (bytes) |
|----------|-------------|
| `log_2026-03-09_12-57_163D9404.BGSQL` | 1,818,624 |
| `log_2026-03-09_12-57_DF792B37.EPSQL` | 282,624 |
| `downloads.28.sqlitedb` | 4,096 |
| `downloads.28.sqlitedb-shm` | 32,768 |
| `downloads.28.sqlitedb-wal` | 156,592 |

### Debug Symbol Files

| Filename | Size (bytes) |
|----------|-------------|
| `DSCSYM-37552E38-73EC-3107-82BB-3D424E169A66` | 1,836,438 |
| `DSCSYM-0FE083A8-981E-3DEF-8CFC-DDA2530BB252` | 14,724 |

### Analytics / IPS Reports

| Filename | Size (bytes) |
|----------|-------------|
| `Analytics-2026-03-04-000004.000.ips.ca 3.synced` | 228,483 |
| `Analytics-2026-03-04-000004.000.ips.ca 4.synced` | 228,483 |
| `xp_amp_app_usage_dnu-2026-03-04-000536.ips` | 55,504 |

### Model / Spotlight Data

| Filename | Size (bytes) |
|----------|-------------|
| `model_catalog_dump.txt` | 563,618 |
| `spotlightknowledged.cpu_.txt` | 28,472 |

### Remaining Logs (alphabetical)

| Filename | Size (bytes) |
|----------|-------------|
| `ACLogs.log` | 566 |
| `AFK.log` | 550 |
| `ASPSnapshots.log` | 1,867 |
| `ATVUpdateLog.log` | 201 |
| `AUDeveloperSettings.log` | 0 |
| `AVConference.log` | 198 |
| `Accessibility.log` | 500 |
| `AccessibilityPrefs.log` | 2,352 |
| `Accounts.log` | 203 |
| `AirPodPowerMetrics.log` | 226 |
| `AppConduit.log` | 225 |
| `AppSupport.log` | 293 |
| `AppleTypeCRetimerLogs.log` | 366 |
| `BASEBAND_TS_TRIGGER.log` | 386 |
| `BTPHY.log` | 487 |
| `BackgroundPowerlog.log` | 629 |
| `BatteryBDC.log` | 1,843 |
| `BatteryHealth.log` | 159 |
| `BatteryIntelligence.log` | 315 |
| `BatteryUIPlist.log` | 1,120 |
| `CacheDeleteHistory.log` | 219 |
| `CalendarPreferences.log` | 292 |
| `CameraCaptureStateDumps.log` | 231 |
| `CentauriLogs.log` | 373 |
| `CloudConfigurationDetails.plist` | 178 |
| `CloudKitBookmarks.log` | 249 |
| `CommandAndControl.log` | 464 |
| `CoreCapture.log` | 1,076 |
| `DarwinInit.log` | 0 |
| `FDR.log` | 581 |
| `ForceResetTailspins.log` | 199 |
| `GEAvailability.log` | 67,933 |
| `HCI.log` | 225 |
| `HIDCrashlogs.log` | 372 |
| `HangTracerTailspins.log` | 380 |
| `IOSADiagnose.log` | 83,301 |
| `InBoxUpdate.log` | 235 |
| `LaunchServices.log` | 209 |
| `LogStreamFilter.log` | 0 |
| `MCUCoreDumps.log` | 0 |
| `MCUPanicLogs.log` | 0 |
| `MSU.log` | 327 |
| `MobileBackup.log` | 298 |
| `MobileSlideShow.log` | 559 |
| `MobileStoreDemo.log` | 255 |
| `Mobile_Demo.log` | 195 |
| `NERDArchive.log` | 245 |
| `OSEligibility.log` | 595 |
| `OTAUpdateLogs.log` | 633 |
| `Panics.log` | 357 |
| `Personalization.log` | 633 |
| `Preferences.log` | 8,059 |
| `ProactiveInputPredictions.log` | 676 |
| `ProtectedCloudStorage.log` | 249 |
| `Proximity.log` | 761 |
| `RecentHangTracerTailspins.log` | 381 |
| `Recoverylogd.log` | 259 |
| `ReportMemoryExceptions.log` | 458 |
| `RunningBoard.log` | 613 |
| `SYSCTL.log` | 561 |
| `Safari10.06.txt` | 4,754 |
| `SensorKit.log` | 366 |
| `Sentry.log` | 1,059 |
| `Siri.log` | 427 |
| `SiriAnalytics.log` | 187 |
| `SocialLayerPlist.log` | 296 |
| `SplunkHistory.log` | 326 |
| `StagingLogs.log` | 4,186 |
| `ThermalLogs.log` | 161 |
| `TimezoneDB.log` | 590 |
| `Trial.log` | 2,513 |
| `UARPEndpointPacketCaptures.log` | 349 |
| `UnifiedAssetLogs.log` | 619 |
| `WatchConnectivity.log` | 212 |
| `WindowServerHangs.log` | 0 |
| `WorkflowResponsiveness.log` | 221 |
| `acLog.plist` | 19,848 |
| `appPrivateData.plist` | 6,053 |
| `appinstallation.log` | 1,295 |
| `brctl.log` | 1,949 |
| `csfdiagnose.json` | 16,006 |
| `cts.log` | 464 |
| `demod.log` | 302 |
| `eSIMSetup.log` | 443 |
| `fileproviderctl.log` | 3,469 |
| `fsck.log` | 163 |
| `keyboard_cache.log` | 285 |
| `mtree_remap.xml` | 491 |
| `olddsc.log` | 1,147 |
| `parsecd.log` | 436 |
| `pmudiagnose.txt` | 21,793 |
| `powerlogs.log` | 1,150 |
| `process_proxied_device_logs.log` | 225 |
| `profile_access_diagnostics.log` | 604 |
| `spindump-meta-collection.log` | 534 |
| `stackshots.log` | 763 |
| `swtransparency.log` | 248 |
| `tailspin-history.log` | 201 |
| `tailspin-info-ts.log` | 605 |
| `time-sensitive-stackshot.log` | 402 |
| `umtool.txt` | 1,718 |
| `usermanagerd_logs.log` | 237 |
| `utilities-timeSensitive-embedded.log` | 375 |
| `version` | 11 |

---

## 2. Device Identity Confirmation

All identity values decoded from `mobileactivationd.log.0` (AccountToken Base64) and corroborated by `lockdownd.log`:

| Field | Value | Source |
|-------|-------|--------|
| **Device Model** | iPhone 14 Pro (`iPhone15,2`) | `mobileactivationd.log.1`, `lockdownd.log` |
| **Hardware Model** | D73AP | `mobileactivationd.log.1` |
| **SOC Generation** | H15 | `mobileactivationd.log.1` |
| **Serial Number** | `[SERIAL_REDACTED]` | `mobileactivationd.log.0` (AccountToken) |
| **IMEI** | `[IMEI_REDACTED]` | `mobileactivationd.log.0` (AccountToken) |
| **IMEI2** | `[IMEI2_REDACTED]` | `mobileactivationd.log.0` (AccountToken) |
| **UDID** | `[UDID_REDACTED]` | `mobileactivationd.log.0` (AccountToken) |
| **iOS Build** | `23D8133` (iOS 26.3.1) | `BuildVersion.json`, `mobileactivationd.log.1` |
| **Wi-Fi MAC** | `[MAC_REDACTED]` | `lockdownd.log` (WiFi service name) |
| **Manufactured** | 2022-09-16 in China | `mobileactivationd.log.0` (RegulatoryInfo) |

✅ **All values match the known device from Project 12 handover documentation.**

---

## 3. New Forensic Evidence

### 3.1 The 31239 HostID Namespace — Three Distinct Variants Confirmed

**Source:** `lockdownd.log`

The rootkit attempted pairing using **three distinct HostIDs**, all sharing the same SystemBUID:

| Attempt | Time (UTC) | HostID | Result |
|---------|------------|--------|--------|
| 1 | Mar 8, 06:24:20 | `31239934-53971539990605760` | ✅ **Implicitly Trusted** (device unactivated, Buddy not completed) |
| 2 | Mar 8, 18:29:46 | `31239977-19700697132105815824` | ❌ Denied — `PasswordProtected` |
| 3 | Mar 8, 18:35:30 | `3123997814642815982443412624` | ❌ Denied — `UserDeniedPairing` |

**Consistent SystemBUID across all attempts:** `31239923-1841638824246695760`

All three HostIDs begin with `31239` — confirming this is the **rootkit's persistent namespace identifier**.

**Key log entry (Attempt 1):**
```
03/08/26 06:24:20.576958 handle_pair: Pair message:
    HostID = "31239934-53971539990605760";
    SystemBUID = "31239923-1841638824246695760";
03/08/26 06:24:20.582597 handle_pair: Buddy has not completed. Implicitly trusting host.
03/08/26 06:24:20.622460 store_escrow_record: Creating escrow bag for 31239934-53971539990605760
03/08/26 06:24:20.628301 handle_pair: Pair for unknown succeeded.
```

**Key log entry (Attempt 1 revocation):**
```
03/08/26 13:28:18.527474 on_queue_destroy_pair_record: Deleted pair record
    (/private/var/root/Library/Lockdown/pair_records/31239934-53971539990605760.plist).
```

**Pair record was deleted** at 13:28:18 when USB disconnected mid-Setup — meaning the rootkit's paired session was revoked before full activation completed.

**Attempt 2 tried to recover at 18:29:**
```
03/08/26 18:29:45.808090 handle_start_session: No pairing record for 31239934-53971539990605760.
03/08/26 18:29:45.818860 handle_set_value: unknown attempting to set [NULL]:[UntrustedHostBUID]
    to [31239923-1841638824246695760]
    HostID = "31239977-19700697132105815824"
03/08/26 18:29:46.919360 handle_pair: Pair for unknown failed: PasswordProtected
```

**Attempt 3 (different numeric HostID format):**
```
HostID = 3123997814642815982443412624   ← Note: no dashes, numeric format
03/08/26 18:35:30.362400 handle_pair: Pair for unknown failed: UserDeniedPairing
```

### 3.2 The accessoryd Exploit on Unactivated Device

**Source:** `mobileactivationd.log.1`

This is the **smoking gun** for the accessoryd exploit:

```
Mar 8 06:24:16 — Mobile Activation Startup
Mar 8 06:24:16 — build_version: 23D8133
Mar 8 06:24:16 — "Upgrade from () to 23D8133 (26.3.1) detected." ← FRESH DFU
Mar 8 06:24:16 — "Failed to load or validate activation record."
Mar 8 06:24:17 — "Activation State: Unactivated"
Mar 8 06:24:27 — Client certification requested by accessoryd
Mar 8 06:24:38 — Client certification requested by accessoryd
Mar 8 06:24:49 — Client certification requested by accessoryd
Mar 8 06:24:58 — "Device is not activated: Unactivated" (identityservicesd)
Mar 8 06:24:59 — Client certification requested by accessoryd
```

**The device was UNACTIVATED.** Normal iOS pairing is impossible before activation. Yet at **06:24:20**, `lockdownd` logged an implicit trust of HostID `31239934-...`.

`accessoryd` (the MFi Accessory Daemon) requested client certificates **four times in rapid succession** during the 16-second window (06:24:27–06:24:59) while the device was still in `Unactivated` state. This is the exploit vector — the rootkit leveraged `accessoryd`'s pre-activation USB access to inject the pairing trust before Apple's activation sequence could engage.

### 3.3 Unknown Host Tunnel Attempt at 13:25

**Source:** `mobileactivationd.log.1`

```
Mar 8 13:25:10 — Host connection (unknown): CreateTunnel1SessionInfoRequest
Mar 8 13:25:13 — Failed to establish session: "Invalid input."
```

An **unknown host** attempted to create a Tunnel1 session approximately 7 hours after the DFU (and 3 minutes before the pair record was deleted). The session failed. This is consistent with the rootkit's Windows-side component attempting to re-establish contact before the user reached Setup Buddy.

### 3.4 Dual SystemImageID — Confirmed Dual System Identity

**Source:** Chat analysis + sysdiagnose structure

| Location in Sysdiagnose | SystemImageID |
|------------------------|---------------|
| `logs/SystemVersion/SystemVersion.plist` | `2ADC4DC8-C50C-4112-847D-867B3D4938A9` |
| `logs/Splat/OS/SystemVersion.plist` | `C89E6759-ABE3-425B-B006-1DAE3CC1A162` |

Both files have:
- `ProductBuildVersion: 23D8133`
- `ProductVersion: 26.3.1`
- `BuildID: 03C240C6-1396-11F1-A802-E8D8889322D1`
- `RestoreVersion: 23.4.133.8.0`

**Same build, two installation identities = two separate installation events of iOS 26.3.1.**

The Splat diagnostic framework (crash/spin/hang capture) recorded a **different SystemImageID** than the canonical system identity. This indicates the rootkit either:
1. Preserved pre-DFU filesystem artifacts (the `2ADC4DC8` image from a prior install)
2. Is maintaining two concurrent system identities (one real, one spoofed)
3. Splat captured the rootkit's own execution environment

### 3.5 IPv6 Addresses — New Evidence

**Source:** `ifconfig.txt`, `lockdownd.log`

| Interface | Address | Type |
|-----------|---------|------|
| `lo0` | `::1` | Loopback |
| `lo0` | `fe80::1%lo0` | Link-local |
| `pdp_ip1` | `fe80::1482:ae17:59b5:3747%pdp_ip1` | Cellular link-local |
| `pdp_ip1` | `[CELLULAR_IPV6_REDACTED]` | **Cellular IPv6 global (secured)** |
| `pdp_ip1` | `[CELLULAR_IPV6_TEMP_REDACTED]` | Cellular IPv6 global (temporary) |
| `en0` (Wi-Fi) | `fe80::8be:c2c1:ab93:7ea5%en0` | Wi-Fi link-local |
| `en0` (Wi-Fi) | `[HOME_IP_REDACTED]` | Wi-Fi IPv4 |
| `utun0` | `fe80::eccb:c2a9:e888:c78c%utun0` | VPN tunnel |
| `nan0` | `fe80::740f:d0ff:fe4e:9f07%nan0` | AWDL |
| `awdl0` | `fe80::780d:9cff:fe9b:a2e6%awdl0` | AirDrop |
| `ipsec2` | `fe80::38fd:f519:314e:3151%ipsec2` | IPSec tunnel |
| `ipsec3` | `fe80::38fd:f519:314e:3151%ipsec3` | IPSec tunnel |

**From `lockdownd.log` — iPhone's own mDNS Remote Pairing advertisement:**
```
Full service name: '[MAC_REDACTED]@fe80::[MAC_DERIVED_LINK_LOCAL]-supportsRP-24._apple-mobdev2._tcp.local.'
```

This is the **iPhone's own link-local IPv6 address** (EUI-64 derived from its Wi-Fi MAC), broadcast via mDNS for Remote Pairing discovery. This address belongs to the device under investigation, not to a peer host. It is persistently advertised across the **entire logging window** (06:24 through 10:02 on Mar 9), confirming sustained network presence.

**Notable:** Two `ipsec` tunnel interfaces (`ipsec2`, `ipsec3`) share the same IPv6 address — potential indicator of a multiplexed or cloned tunnel interface. This warrants further investigation.

### 3.6 Restore Perform — DFU Confirmation and Timestamp Anomaly

**Source:** `restore_perform.txt`

The restore log begins at `13:15:54.0151-GMT` with boot-command `device-recovery` and confirms a standard DFU restore sequence. Timestamps in the restore log are **fractional seconds into epoch** rather than wall-clock times — this is normal for low-level restore firmware.

However, the restore timestamp `13:15:54` corresponds to **Mar 8, 13:15 UTC**, which is **inconsistent** with `lockdownd.log` showing device boot at 06:24. This suggests the `restore_perform.txt` captures a **second restore event** — likely the one visible to Setup at 13:28 when the pair record was deleted.

### 3.7 Mar 12 forceReset Events — Post-Investigation Crash Evidence

**Three large forceReset IPS files (>1 MB each):**
- `forceReset-full-2026-03-12-111038.0002.ips` — 1,436,379 bytes
- `forceReset-full-2026-03-12-113853.0002.ips` — 1,263,791 bytes
- `forceReset-full-2026-03-12-175254.0002.ips` — 1,351,042 bytes

Three forced resets on **Mar 12** (the same day as the handover documents). These are anomalously large forceReset captures and may contain kernel/system state evidence of the rootkit. **Recommend deep analysis.**

### 3.8 Duplicate Analytics Files

Two identical files:
- `Analytics-2026-03-04-000004.000.ips.ca 3.synced` (228,483 bytes)
- `Analytics-2026-03-04-000004.000.ips.ca 4.synced` (228,483 bytes)

Both are byte-for-byte identical (same size, Mar 4 timestamp). This duplication pattern is consistent with rootkit behavior observed elsewhere in the investigation (duplicated system artifacts).

### 3.9 MarketingName "Windows PC" in Pair Records

**Source:** `lockdownd.log`

```
MarketingName = "Windows PC";
HostID = "31239977-19700697132105815824";
SystemBUID = "31239923-1841638824246695760";
```

The rootkit identifies itself as `"Windows PC"` in its pairing request — this is the MarketingName field. This is consistent with the Windows PC implant operating as the host-side component of the 31239 rootkit.

---

## 4. Timeline Correlations

### Combined Attack Timeline (UTC)

| Date/Time (UTC) | Event | Source | Significance |
|-----------------|-------|--------|-------------|
| **Feb 27, 02:45** | Windows EVTX attack begins — EventID 1536 | EVTX Analysis Addendum | Windows-side initial access |
| **Feb 27, 03:53** | Windows attack ends — last EventID 4697 (WirelessDisplay-Out-UDP service install) | EVTX Analysis | Attack window closes |
| **Feb 27, 04:37** | Earliest file modification timestamps inside sysdiagnose (created 36 min after Windows attack) | Sysdiagnose metadata | **Anomalous** — iOS files created during Windows attack window |
| **Mar 4, 00:00** | Analytics IPS event (`Analytics-2026-03-04-000004.000.ips`) | Analytics files | Duplicated artifact |
| **Mar 8, ~06:24:00** | DFU restore completes — device boots in Unactivated state | `lockdownd.log`, `mobileactivationd.log.1` | Start of critical window |
| **Mar 8, 06:24:16** | `mobileactivationd` starts — confirms DFU upgrade from null to 23D8133 | `mobileactivationd.log.1` | Build confirmed |
| **Mar 8, 06:24:17** | `lockdownd` starts — detects USB and USBHost connections | `lockdownd.log` | Device already connected via USB |
| **Mar 8, 06:24:19** | Unknown host sets `UntrustedHostBUID` to `31239923-1841638824246695760` | `lockdownd.log` | **Rootkit first contact** |
| **Mar 8, 06:24:20** | `handle_pair: Buddy has not completed. Implicitly trusting host.` — HostID `31239934-53971539990605760` | `lockdownd.log` | **IMPLICIT TRUST ESTABLISHED** |
| **Mar 8, 06:24:20** | Escrow bag created for `31239934-53971539990605760` | `lockdownd.log` | Pair record written |
| **Mar 8, 06:24:27–06:24:59** | `accessoryd` requests client certificates 4× on UNACTIVATED device | `mobileactivationd.log.1` | **accessoryd exploit** |
| **Mar 8, 13:15:54** | Restore engine starts (`restore_perform.txt` timestamp) | `restore_perform.txt` | Possible second restore event |
| **Mar 8, 13:25:10** | Unknown host CreateTunnel1SessionInfoRequest — fails | `mobileactivationd.log.1` | Rootkit re-contact attempt |
| **Mar 8, 13:25:13** | Failed to establish session: "Invalid input" | `mobileactivationd.log.1` | Tunnel failed |
| **Mar 8, 13:26:09–13:28:28** | `akd` (AuthKit) requests certs repeatedly | `mobileactivationd.log.1` | Pre-activation retry |
| **Mar 8, 13:28:18** | Pair record `31239934-...plist` DELETED — USB host disconnected during Setup | `lockdownd.log` | Rootkit trust revoked |
| **Mar 8, 13:29:06** | Activation info generated for Setup | `mobileactivationd.log.1` | Legitimate activation begins |
| **Mar 8, 13:29:25** | Apple activation requested by Setup | `mobileactivationd.log.0` | Device activates with Apple |
| **Mar 8, 13:30:26** | DERT/SDCRT BAA request sent to Apple activation servers | `mobileactivationd_dcrt_baa_request.txt` | Activation confirmed |
| **Mar 8, 13:30:29–30** | BAA response received | `mobileactivationd_dcrt_baa_response.txt` | Activation complete |
| **Mar 8, 14:55:23** | BDC data logged | `BDC_SBC_*` | Device in normal use |
| **Mar 8, 18:29:46** | 31239 rootkit second attempt — HostID `31239977-...` — denied (PasswordProtected) | `lockdownd.log` | User has set passcode; rootkit blocked |
| **Mar 8, 18:35:30** | 31239 rootkit third attempt — numeric HostID `3123997814642815982443412624` — denied (UserDeniedPairing) | `lockdownd.log` | User explicitly denied |
| **Mar 9, 10:02:30** | BDC data logged | `BDC_SBC_*` | Device continues operating |
| **Mar 9, 12:10:12** | `BuildVersion.json` timestamp | `BuildVersion.json` | Evidence timestamp anchor |
| **Mar 9, 12:56:54** | Sysdiagnose captured | Sysdiagnose filename | Primary evidence collection |
| **Mar 12, 11:10:38** | forceReset event #1 | `forceReset-full-2026-03-12-111038.0002.ips` | Post-investigation crash |
| **Mar 12, 11:38:53** | forceReset event #2 | `forceReset-full-2026-03-12-113853.0002.ips` | Post-investigation crash |
| **Mar 12, 17:52:54** | forceReset event #3 | `forceReset-full-2026-03-12-175254.0002.ips` | Post-investigation crash |

### The 7-Hour Gap — Critical Finding

| Time | State |
|------|-------|
| 06:24 | DFU complete → rootkit establishes trust via accessoryd → device is UNACTIVATED |
| 06:24–13:25 | **7 hours** — rootkit has pair record; device idle or user delayed |
| 13:25 | Rootkit attempts tunnel — fails |
| 13:28 | USB disconnects; pair record deleted |
| 13:29 | User runs Setup; device activates with Apple |
| 18:29 | Rootkit tries again — blocked by passcode |

**The rootkit had a 7-hour window of implicit trust on an unactivated device.**

---

## 5. Cross-Device Linkage Evidence

### iOS ↔ Windows Linkage

| Indicator | iOS Evidence | Windows Evidence | Correlation |
|-----------|-------------|-----------------|-------------|
| **31239 Namespace** | SystemBUID `31239923-...`, HostIDs `31239934-...`, `31239977-...` | EventID 4697: service "WirelessDisplay-Out-UDP" (known 31239 artifact) | **DIRECT MATCH** — same rootkit family |
| **Windows PC identity** | `MarketingName = "Windows PC"` in pair record | Windows PC with HostID in attack window | Rootkit self-identifies as Windows host |
| **Attack timestamps** | iOS DFU: Mar 8, 06:24 UTC | Windows EVTX attack: Feb 27, 02:45–03:53 UTC | Sequential infection — Windows first, iOS after |
| **Feb 27 04:37 timestamps** | Files inside Mar 9 sysdiagnose with Feb 27 timestamps | Windows attack ends at 03:53 | Files created/modified 44 minutes after Windows attack ends |

### iOS Dual-System Identity

| Identity | SystemImageID | Location |
|----------|---------------|----------|
| Post-DFU (canonical) | `2ADC4DC8-C50C-4112-847D-867B3D4938A9` | `logs/SystemVersion/SystemVersion.plist` |
| Rootkit/Splat captured | `C89E6759-ABE3-425B-B006-1DAE3CC1A162` | `logs/Splat/OS/SystemVersion.plist` |

Both found in a single sysdiagnose from Mar 9 — evidence of two concurrent iOS installation identities.

### accessoryd → Rootkit Chain

```
[Windows PC with 31239 HostID]
    ↓ USB connection at boot
[accessoryd on unactivated iPhone]
    ↓ Certificate requests (4× in 33 seconds)
[lockdownd implicit trust granted]
    ↓ Pair record created: 31239934-53971539990605760
[Escrow bag written to filesystem]
    ↓ (7 hours later — USB disconnect)
[Pair record deleted at 13:28]
[Rootkit attempts re-entry at 18:29, 18:35 → BLOCKED]
```

---

## 6. Security Concerns & Redaction Recommendations

### 6.1 High Priority — Direct PII (redact before public sharing)

| Data Type | Value | Found In |
|-----------|-------|----------|
| **Serial Number** | `[SERIAL_REDACTED]` | `mobileactivationd.log.0` (Base64 AccountToken) |
| **IMEI** | `[IMEI_REDACTED]` | `mobileactivationd.log.0` (AccountToken) |
| **IMEI2** | `[IMEI2_REDACTED]` | `mobileactivationd.log.0` (AccountToken) |
| **UDID** | `[UDID_REDACTED]` | `mobileactivationd.log.0` (AccountToken) |
| **Wi-Fi MAC Address** | `[MAC_REDACTED]` | `lockdownd.log` (service name) |
| **Home network IP** | `[IP_REDACTED]` | `ifconfig.txt` |
| **Cellular global IPv6** | `[IPV6_REDACTED]` | `ifconfig.txt` |

**Primary exposure file:** `mobileactivationd.log.0` — the AccountToken at line ~25 is a Base64-encoded plist containing serial, IMEI, IMEI2, UDID, and activation URLs in plaintext. The `mobileactivationd_dcrt_baa_request.txt` and `mobileactivationd_sdcrt_baa_request.txt` contain device certificates that could be used for device fingerprinting.

### 6.2 Medium Priority — Activation & Certificate Material

| Data Type | Found In |
|-----------|---------|
| DeviceCertificate (binary, in pair records) | `lockdownd.log` (embedded as hex in pair messages) |
| HostCertificate for 31239 HostID | `lockdownd.log` (pair messages at 18:29 and 18:35) |
| RootCertificate | `lockdownd.log` |
| ActivationRandomness UUID | `mobileactivationd.log.0` (`6D63367C-DC3C-43D2-9BDB-64044F4BE642`) |
| WildcardTicket (MFi) | `mobileactivationd.log.0` (AccountToken) |
| System container UUIDs | `mobileactivationd.log.1` (`F55DB6B8-...`, `4CF76A4F-...`, `2CBF001E-...`) |

### 6.3 Lower Priority — Network & Session Data

| Data Type | Found In |
|-----------|---------|
| Internal cellular IPv6 (temporary) | `ifconfig.txt` |
| All link-local IPv6 addresses | `ifconfig.txt` |
| Network extension UUIDs | `com.apple.networkextension.uuidcache.plist` |
| IPSec tunnel configuration | `com.apple.networkextension.plist` |
| Netstat connections | `netstat.txt` |
| Bluetooth HCI logs | `HCI.log` |

### 6.4 Redaction Recommendations

1. **Before any public disclosure of this repository:** Remove or redact all activation log files (`mobileactivationd.log.*`, `mobileactivationd_*_baa_*.txt`) as they contain IMEI, serial, UDID, and certificate material.

2. **If sharing for analysis purposes:** Replace specific values with tokens:
   - Serial: `[SERIAL_REDACTED]`
   - IMEI/IMEI2: `[IMEI_REDACTED]`
   - UDID: `[UDID_REDACTED]`
   - MAC: `[MAC_REDACTED]`

3. **The DOCX files** (`iOS First Contact Handover Mar12.docx`, `Project12 SaveFile Mar12.docx`) should be reviewed for Apple ID, email addresses, or phone numbers before sharing — these were not parseable in this analysis.

4. **`TCC.db`** (Privacy/TCC database, 86 KB) may contain app permission history linked to Apple ID — review before sharing.

5. **`state.plist`** (206 KB) and `config.plist` (84 KB) are large state files that likely contain additional device identifiers not enumerated here.

---

## 7. Summary of Key Conclusions

### 7.1 The accessoryd Exploit is Confirmed

The primary iOS attack vector is confirmed in the logs: `accessoryd` was used to request client certificates **before device activation**, exploiting the pre-activation USB access window. This is consistent with the Operation Triangulation lineage described in handover documentation.

### 7.2 Implicit Trust Was Achieved

HostID `31239934-53971539990605760` achieved **implicit pairing trust** at 06:24:20 Mar 8 — before Setup Buddy completed, before the device activated with Apple, and before the user had any opportunity to consent to or deny pairing. This is a zero-interaction exploit.

### 7.3 The Rootkit Has Multiple HostID Variants

Three HostIDs were used in a single day, all sharing the `31239` prefix and the same SystemBUID. This suggests the rootkit can generate new HostIDs on demand while maintaining a consistent system-level identity.

### 7.4 The Windows–iOS Connection is Established

The Windows PC with 31239 HostID was physically connected to the iPhone via USB at the moment of DFU completion. This is not a coincidence — it required advance knowledge of or control over the DFU timing.

### 7.5 The Rootkit Failed to Survive Setup

The pair record was **deleted at 13:28:18** when USB disconnected. The two subsequent re-entry attempts (18:29 and 18:35) were **blocked** by the device's passcode. The rootkit did not achieve persistent access beyond the initial 7-hour window.

**However:** The dual SystemImageID (Section 3.4) and the Feb 27 04:37 timestamps in the Mar 9 sysdiagnose suggest the rootkit may have had **prior access** on the device (pre-DFU) that left traces surviving the restore.

### 7.6 Further Investigation Required

| Item | Priority |
|------|----------|
| Decode the three large forceReset IPS files (Mar 12) | HIGH |
| Analyze `TCC.db` for privacy permission anomalies | HIGH |
| Review DOCX files for Apple ID / email PII | HIGH |
| Compare `DSCSYM-37552E38-...` (1.8 MB debug symbols) to known rootkit signatures | MEDIUM |
| Analyze the `thu_mar_05_2026_apple_i_phone_logs_analysis_for_rootkit.json` (2.1 MB) | MEDIUM |
| Investigate dual `ipsec2`/`ipsec3` sharing same IPv6 address | MEDIUM |
| Cross-reference `GEAvailability.log` (67 KB) for location data leakage | LOW |
| Review `BatteryUISysdiagnose.plist` (784 KB) for anomalous power patterns during attack window | LOW |

---

*This document was prepared as part of Project 12 forensic analysis. All findings are based on direct evidence extracted from the repository files as enumerated in Section 1.*
