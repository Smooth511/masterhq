# Windows Install Interception Analysis - 2026-03-19

**Status:** COLLECTING - Batch upload in progress (7/16 images received)

**Context:** User documenting malware persistence during Windows install interception. Fresh install showing immediate compromise indicators.

---

## Hunt Targets

- **Tracer UIDs:** 33554432, 50331648, 51150848
- **OneSettings queries**
- **Network profile manipulation**
- **Suspicious processes**
- **C2 addresses**
- **Policy entries**
- **Registry manipulation**

---

## Evidence Received

| # | Filename | Status | Key Findings |
|---|----------|--------|--------------|
| 1 | IMG_0253 | RECEIVED | Network profile registry entries |
| 2 | IMG_0254 | RECEIVED | Registry entries - paths and values |
| 3 | IMG_0255 | RECEIVED | TBD |
| 4 | IMG_0256 | RECEIVED | TBD |
| 5 | IMG_0257 | RECEIVED | TBD |
| 6 | IMG_0258 | RECEIVED | TBD - Image 6 |
| 7 | IMG_0259 | RECEIVED | TBD - Image 7 |
| 8-16 | Pending | WAITING | 9 more incoming |

---

## Preliminary Analysis

### Image 1 (IMG_0253) - Network Profiles

**Registry Path:** `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\NetworkList`

Observed:
- Multiple NetworkProfile entries with different GUIDs
- Category settings being manipulated
- Profile creation timestamps need cross-reference with system first boot

**Significance:** Fake network profiles are a persistence mechanism. Malware creates profiles to:
1. Trigger network-based persistence on connection
2. Modify firewall rules per-profile
3. Evade detection by creating "known" networks

### Image 2-7 - Pending Full Analysis

Content received but requires OCR pass for detailed extraction.

---

## Known Indicators (from prior investigation)

From Mini-Tank-MKII machine:
- PID 3992 → 109.61.19.21:80 (G-Core Labs London)
- PID 1052 → 85.234.74.60:80
- Windows Security blocked by IT policy on fresh install

---

## Next Steps

1. Receive remaining 9 images
2. OCR pass on all images
3. Cross-reference UIDs
4. Map registry entries to known malware families
5. Timeline reconstruction

---

## Image URLs (for reference)

- IMG_0253: 4d7a5e05-2f5f-408c-859f-9b89b6f36366
- IMG_0254: 02b03e4b-aae6-4bc3-8fad-d44bbb878912
- IMG_0255: 4aa25da7-1b51-412a-b68d-ef71346b1bf8
- IMG_0256: ecfcd578-5771-487c-a624-a415cba26dc7
- IMG_0257: e3c6e080-28f9-42ef-bbfc-081bb0ea9b49
- IMG_0258: b41c54fb-898e-42e5-a580-97a6f09948e8
- IMG_0259: 2d3cf9b1-7d5b-4d50-9459-4ff00b480d54
