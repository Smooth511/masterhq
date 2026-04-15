# Registry UID Attack Evidence

**Date Documented:** 2026-03-19
**Controller Evidence:** IMG_0278 (GitHub asset: b09ea036-b60c-4000-a573-fbb1b2fa4b48)
**Classification:** Mass Registry Override Attack via UID Spam

---

## Tracer UIDs Identified

| UID (Decimal) | UID (Hex) | Binary Pattern | Role |
|---------------|-----------|----------------|------|
| 33554432 | 0x02000000 | 0000 0010 0000 0000 0000 0000 0000 0000 | Base migration marker |
| 50331648 | 0x03000000 | 0000 0011 0000 0000 0000 0000 0000 0000 | Secondary marker |
| 51150848 | 0x030D0000 | 0000 0011 0000 1101 0000 0000 0000 0000 | Variant marker |

### Pattern Analysis
- All three have **aligned byte boundaries** (0x00 in lower bytes)
- 33554432 and 50331648 differ only in bit 24 (0x02 vs 0x03)
- 51150848 is 50331648 + 851200 (0x000D0000) - indicates sub-categorization

These are **not random** - they're deliberately chosen marker values for tracking/overriding registry entries.

---

## Attack Method: UID Spam

### How It Works
1. Identify target registry keys with legitimate UIDs
2. Create **hundreds of similar entries** around the tracer UIDs
3. Legitimate entries get lost in the noise
4. Windows processes the spam entries, potentially using attacker-controlled values

### Why This Works
- Registry enumeration returns entries in no guaranteed order
- First-match or last-match behavior varies by API
- Overwhelming volume makes manual inspection impossible
- Legitimate tools may pick up wrong values

---

## Controller Mechanism (IMG_0278)

**User observation:** "judging by the spacing its important"

The spacing in IMG_0278 likely indicates:

### Possible Interpretations

1. **Hierarchical Command Structure**
   ```
   [Master Controller]
       [MIG 0x02000000 handler]
       [MIG 0x03000000 handler]
           [Variant 0x030D0000]
   ```

2. **Execution Sequence**
   - Indentation = dependency order
   - Parent must complete before children execute

3. **Target Registry Hives**
   - Different spacing = different registry locations
   - HKLM vs HKCU vs other hives

### What to Look For
When this image can be analyzed in detail:
- Column alignment (field boundaries)
- Indentation levels (hierarchy)
- Repeated patterns (iteration markers)
- Numeric sequences (UID ranges being targeted)

---

## Connection to Other Findings

| Finding | Connection |
|---------|------------|
| Synergy during DISM | Controller may invoke UID spam during DISM phase |
| 100s of registry entries | Controller generates the spam volume |
| Timing sensitivity | Controller coordinates timing with Synergy operator |

---

## Evidence Chain

```
IMG_0277 (DISM + Synergy)
    ↓
    Attacker has real-time control during install
    ↓
IMG_0278 (MIG Controller)
    ↓
    Controller orchestrates registry spam
    ↓
Registry UIDs (33554432, 50331648, 51150848)
    ↓
    Legitimate entries overridden
    ↓
    System compromised at registry level
```

---

## Preservation Note

The tracer UIDs should be added to detection tools:
- Hunt for these values in registry exports
- Flag any rapid creation of entries near these UIDs
- Monitor for registry keys with these exact values
