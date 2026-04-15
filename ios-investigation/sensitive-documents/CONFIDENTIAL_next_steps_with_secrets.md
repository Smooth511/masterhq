# CONFIDENTIAL — Next Steps with Redacted-String Context
## Investigator Instructions: Project 12

**Classification:** Restricted — Investigator Use Only  
**Contains:** References to redaction tokens (no actual secrets in this file)  
**Date:** 2026-03-13  

> This document cross-references redaction tokens used in the public-safe artefacts
> with the investigative queries that require the original values. Obtain the actual
> values from `CONFIDENTIAL_sensitive_mapping_Forensic_diagnosis.md` (stored
> separately, not committed to this repository).
>
> **Do not share this document with parties outside the investigation team.**

---

## Part 1 — Carrier / Network Queries

### 1.1 Cellular Session Records

**Token:** `[IMEI_REDACTED]`, `[CELLULAR_IPV6_REDACTED]`  
**Reason:** Verify whether there was unusual cellular activity during the attack window.

**Queries to run using the original values from confidential mapping:**

```text
CARRIER QUERY (submit via lawful channel / IMEI request):
  Device IMEI: [IMEI_REDACTED]
  Period: 2026-03-08 06:00 UTC to 2026-03-08 19:00 UTC
  Requested records:
    - Session start/end times (PDN activation/deactivation)
    - Data volume per session
    - Cell tower assignments (cell ID, lat/lng) for location correlation
    - Any incoming connections to [CELLULAR_IPV6_REDACTED] during window
```

**Why:** During the 7-hour rootkit window (06:24–13:28), it is unknown whether
the device transmitted data over cellular. If the rootkit exfiltrated data, it
would appear as anomalous cellular data sessions during this window.

### 1.2 Wi-Fi / Home Router Logs

**Token:** `[HOME_IP_REDACTED]`, `[MAC_REDACTED]`  
**Reason:** Identify what hosts communicated with the device on the home network.

```text
ROUTER QUERY:
  Device MAC: [MAC_REDACTED]
  Home IP: [HOME_IP_REDACTED]
  Period: 2026-03-08 06:00 to 2026-03-08 19:00 UTC
  AND: 2026-03-12 09:00 to 2026-03-13 04:00 UTC
  Requested records:
    - DHCP lease history for [MAC_REDACTED]
    - ARP table entries showing which hosts communicated with [HOME_IP_REDACTED]
    - Firewall/connection logs — specifically outbound connections from [HOME_IP_REDACTED]
    - DNS queries originating from [MAC_REDACTED]
```

**Why:** The rootkit's Windows PC must have been on the same network (or USB).
Router logs will show which devices were present and communicated with the iPhone
during both the attack window (Mar 8) and the diagnostic session (Mar 12).

---

## Part 2 — Device Identifier Queries

### 2.1 Apple Device Lookup / PSIRT Submission

**Tokens:** `[SERIAL_REDACTED]`, `[UDID_REDACTED]`, `[IMEI_REDACTED]`

```text
APPLE PSIRT SUBMISSION (product-security@apple.com):
  Subject: iOS pairing vulnerability exploitation — 31239 namespace rootkit
  Device serial: [SERIAL_REDACTED]
  Device UDID: [UDID_REDACTED]
  Device IMEI: [IMEI_REDACTED]
  iOS build: 23D8133 (26.3.1)
  
  IOCs:
  - HostID: 31239934-53971539990605760
  - HostID: 31239977-19700697132105815824  
  - HostID: 3123997814642815982443412624
  - SystemBUID: 31239923-1841638824246695760
  - MarketingName reported by rootkit: "Windows PC"
  - Attack vector: lockdownd implicit pairing on unactivated device (pre-Setup Buddy)
  - accessoryd requested client certificates 4× in 33 seconds on unactivated device
  
  Request:
  1. Confirm whether iOS 26.3.1 (23D8133) contains a patch for the implicit 
     pairing path (Buddy not completed → implicitly trusting host)
  2. Confirm whether any certificates associated with [SERIAL_REDACTED] / 
     [UDID_REDACTED] should be revoked
  3. Cross-reference 31239 HostID namespace against internal threat intelligence
```

### 2.2 CrashReporter Key — Device Fingerprint

**Token:** `[CRASHREPORTER_KEY_REDACTED]`

The CrashReporter Key uniquely identifies this device in Apple's crash reporting
system. Do NOT include it in any public submission. When submitting crash reports
to Apple for this device, it will appear automatically — ensure the submission
channel is private/confidential.

```text
INTERNAL RECORD ONLY:
  CrashReporter Key: [CRASHREPORTER_KEY_REDACTED]
  Use: Cross-reference with Apple diagnostic backend if Apple PSIRT requests 
       device-specific telemetry verification.
  Do not: Include in any public GitHub issue, PR, or forum post.
```

---

## Part 3 — March 12 Session Verification

### 3.1 Confirm the Host Identity of the `remotepairingdeviced` Session

**Critical question:** What HostID was connected to the device during the
March 12 session? Was it the investigator's Mac, or a 31239-prefix rootkit ID?

```text
INVESTIGATION STEP (internal):
  1. Locate the investigator's Mac that connected to the device on March 12
  2. On that Mac, open Terminal and run:
       defaults read /var/db/lockdown/<DEVICE_UDID>.plist
     (Replace <DEVICE_UDID> with [UDID_REDACTED] from the confidential mapping)
  3. The HostID recorded in that plist should match what lockdownd.log shows 
     for March 12 — it should be a standard UUID format (e.g., 
     XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX in hexadecimal)
  4. If the HostID starts with "31239", the session was NOT the investigator's Mac.
     Escalate immediately.

  ALTERNATIVELY: Pull lockdownd.log from the device as of March 12:
    - Connect device to trusted Mac
    - Run: idevicesyslog -u <UDID> | grep "handle_pair\|HostID\|handle_start_service"
    - Or: Use Apple Configurator 2 → Prepare → check Device Logs
```

### 3.2 Session Duration Window for Evidence Queries

```text
March 12 session window for log/PCAP queries:
  Start:  2026-03-12 10:03:49 UTC  (Boot #1 / session established)
  End:    2026-03-13 02:00–03:00 UTC (estimated, ~16h duration)
  
  Sub-windows of interest:
  - Boot #1 to Panic #1:  10:03:49 – 11:10:38 UTC  (~67 min)
  - Boot #2 to Panic #2:  11:10:32 – 11:38:53 UTC  (~28 min)
  - Gap (device off?):    11:38:53 – 16:36:15 UTC  (~5h)
  - Boot #3 to Panic #3:  16:36:15 – 17:52:54 UTC  (~77 min)
  - Post-panic session:   17:52:54 – ~02:00 Mar 13 (~8h remaining)
```

---

## Part 4 — Certificate / Activation Material

### 4.1 Device Certificates in lockdownd.log

The `lockdownd.log` (141 KB) contains hex-embedded pair record data at the 18:29
and 18:35 entries. These include:
- DeviceCertificate (device identity certificate)
- HostCertificate for the 31239 HostID (the rootkit's certificate)
- RootCertificate

```text
EXTRACTION STEPS:
  1. Open lockdownd.log and search for the 18:29:45 and 18:35:30 entries
  2. Find lines starting with "DeviceCertificate = <" — the hex data between 
     < and > is the DER-encoded certificate
  3. Convert hex to binary: echo "<hex_string>" | xxd -r -p > device_cert.der
  4. Inspect: openssl x509 -in device_cert.der -inform DER -noout -text
  5. The HostCertificate from the 31239 HostID may reveal the rootkit's PKI chain
     — submit to Apple PSIRT and national CERT
```

### 4.2 ActivationRandomness UUID

**Token:** `[ACTIVATION_RANDOMNESS_UUID]`

This UUID is used in Apple's activation challenge/response. The original value
is in the confidential mapping. Do not reuse it or share it — it could be used
to replay aspects of the activation context.

### 4.3 IMEI — Carrier Reporting for Possible SIM Cloning

**Token:** `[IMEI_REDACTED]`, `[IMEI2_REDACTED]`

If the rootkit had access to the device during the 7-hour unactivated window,
it may have read IMEI values for SIM cloning or carrier tracking.

```text
CARRIER ACTION:
  Contact carrier using [IMEI_REDACTED] to:
  1. Request IMEI block list check — was this IMEI reported to GSMA IMEI DB?
  2. Request session records for the attack window (see Part 1)
  3. Consider requesting an IMEI change if the carrier supports it
```

---

## Part 5 — Windows-Side Investigation

### 5.1 EVTX Service Binary Hash

The EVTX Analysis addendum references a service "WirelessDisplay-Out-UDP"
installed via EventID 4697. The service binary path is in the EVTX event.

```text
HASH AND SUBMIT:
  1. Extract the full EventID 4697 entry from the Windows EVTX file
  2. Note the ServiceFileName field (path to the service executable)
  3. Hash the file: Get-FileHash <path> -Algorithm SHA256
  4. Submit hash to VirusTotal: https://www.virustotal.com
  5. If detected, note the malware family and add to IOC list
  6. If NOT detected (potential novel malware), submit for analysis to:
     - Microsoft Security Response Center (MSRC): www.microsoft.com/msrc
     - Apple PSIRT (for Windows↔iOS rootkit context)
     - Your national CERT
```

### 5.2 Windows Timeline Query for 31239 Activity

```text
WINDOWS LOG SEARCH:
  Time window: 2026-02-27 02:45 to 2026-03-08 06:24 UTC
  
  Search for:
  - EventID 4697 (service install) — any with service names containing "31239"
  - EventID 7045 (System log, new service install)
  - EventID 4688/4624 (process creation / logon) — look for suspicious binaries
  - EventID 5156/5158 (Windows Filtering Platform — network connections) from 
    the service process
  - Registry HKLM\SYSTEM\CurrentControlSet\Services\WirelessDisplay-Out-UDP 
    (verify if still present; if so, capture and delete)
  
  SIEM query example (adapt for your platform):
  EventID = 4697 AND TimeCreated >= "2026-02-27T02:00:00Z" 
  AND TimeCreated <= "2026-03-08T07:00:00Z"
```

---

## Part 6 — Evidence Preservation

### 6.1 Files to Archive Before Any Further Access

The following files in the repository contain unredacted PII or sensitive material
that must be preserved in controlled storage before any further disclosure:

| File | Sensitive Content | Action |
|------|------------------|--------|
| `lockdownd.log` | MAC address (`[MAC_REDACTED]`) in line 88; hex-embedded device certificates | Archive encrypted copy; scrub MAC from any shared version |
| `mobileactivationd.log.0` | Serial, IMEI, UDID, IMEI2 in Base64 AccountToken | Archive encrypted copy; do NOT share publicly |
| `mobileactivationd_dcrt_baa_request.txt` | 72 KB device certificate material | Archive encrypted; needed for certificate fingerprinting |
| `mobileactivationd_sdcrt_baa_request.txt` | 72 KB device certificate material | Same as above |
| `forceReset-full-2026-03-12-*.ips` (all 3) | CrashReporter Key (`[CRASHREPORTER_KEY_REDACTED]`) | Archive; redact key before any sharing |
| `ResetCounter-2026-03-12-*.ips` (both) | CrashReporter Key | Same as above |

### 6.2 Repository Access Control

```text
MAINTAINER ACTION:
  If this repository is or will become public, ensure the following are NOT 
  publicly accessible:
  
  Option A — Remove from history (destructive):
    git filter-branch --force --index-filter \
      "git rm --cached --ignore-unmatch lockdownd.log mobileactivationd.log.0 \
       mobileactivationd_dcrt_baa_request.txt mobileactivationd_sdcrt_baa_request.txt" \
      --prune-empty --tag-name-filter cat -- --all
    (Run this only if you have confirmed a full secure backup exists)
  
  Option B — Add to .gitignore and rotate all secrets/certs:
    Add these files to .gitignore to prevent future commits.
    Treat all already-committed material as compromised.
  
  Option C — Keep repository private:
    Ensure repository visibility remains private.
    Add branch protection and require review for any visibility change.
```

---

## Part 7 — Investigation Timeline Windows for Evidence Requests

Summary of time windows for all evidence requests:

| Window | UTC Range | Purpose |
|--------|-----------|---------|
| Windows attack window | 2026-02-27 02:45 – 03:53 | Initial Windows-side access |
| Anomalous iOS files | 2026-02-27 04:37 | iOS files created post-Windows attack |
| Analytics duplication | 2026-03-04 00:00 | Duplicate artefact creation |
| iOS DFU + rootkit window | 2026-03-08 06:00 – 13:29 | Primary attack and 7-hour trust window |
| Rootkit re-entry attempts | 2026-03-08 18:29 – 18:36 | Blocked attempts post-passcode |
| Normal device use | 2026-03-08 13:29 – 2026-03-09 12:56 | Baseline for comparison |
| **March 12 diagnostic session** | **2026-03-12 10:03 – ~Mar 13 02:00** | **16-hour session — identity unconfirmed** |

---

*This document contains no actual secrets or PII. All sensitive values are
referenced by redaction tokens only. Retrieve original values from
`CONFIDENTIAL_sensitive_mapping_Forensic_diagnosis.md` stored in your
secure vault.*

*Generated: 2026-03-13 as part of Project 12 automated forensic review.*
