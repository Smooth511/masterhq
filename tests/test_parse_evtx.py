"""Tests for tools/parse_evtx.py — the EVTX parsing logic.

These tests exercise the pure-Python helper functions without requiring
actual .evtx files (the evtx library dependency is only needed for full
file parsing).
"""

import sys
import types

# parse_evtx does sys.exit(1) if `evtx` isn't installed. We stub the
# evtx module so the helpers can be imported without the native library.
if "evtx" not in sys.modules:
    _stub = types.ModuleType("evtx")
    _stub.PyEvtxParser = None  # type: ignore[attr-defined]
    sys.modules["evtx"] = _stub

from parse_evtx import (
    SECURITY_EVENTS,
    _normalize_event_data,
    get_event_data,
    get_event_id,
    pid_hex_variants,
    _pid_in_fields,
)


# ---------------------------------------------------------------------------
# get_event_id
# ---------------------------------------------------------------------------

class TestGetEventId:
    def test_plain_int(self):
        data = {"Event": {"System": {"EventID": 4688}}}
        assert get_event_id(data) == 4688

    def test_string_int(self):
        data = {"Event": {"System": {"EventID": "7045"}}}
        assert get_event_id(data) == 7045

    def test_dict_with_text_key(self):
        """Some EVTX records store EventID as {'#text': '4688', 'Qualifiers': '0'}."""
        data = {"Event": {"System": {"EventID": {"#text": "4688", "Qualifiers": "0"}}}}
        assert get_event_id(data) == 4688

    def test_missing_event_id(self):
        assert get_event_id({}) == 0
        assert get_event_id({"Event": {}}) == 0
        assert get_event_id({"Event": {"System": {}}}) == 0

    def test_bad_value_returns_zero(self):
        data = {"Event": {"System": {"EventID": "not_a_number"}}}
        assert get_event_id(data) == 0

    def test_none_value(self):
        data = {"Event": {"System": {"EventID": None}}}
        assert get_event_id(data) == 0


# ---------------------------------------------------------------------------
# _normalize_event_data
# ---------------------------------------------------------------------------

class TestNormalizeEventData:
    def test_flat_dict_passthrough(self):
        evdata = {"NewProcessId": "0x41c", "NewProcessName": "cmd.exe"}
        assert _normalize_event_data(evdata) == evdata

    def test_data_array_form(self):
        evdata = {
            "Data": [
                {"@Name": "NewProcessId", "#text": "0x41c"},
                {"@Name": "NewProcessName", "#text": "cmd.exe"},
            ]
        }
        result = _normalize_event_data(evdata)
        assert result["NewProcessId"] == "0x41c"
        assert result["NewProcessName"] == "cmd.exe"

    def test_data_array_with_strings(self):
        """Plain string entries in Data array should be skipped."""
        evdata = {"Data": ["some raw string", {"@Name": "Key", "#text": "Val"}]}
        result = _normalize_event_data(evdata)
        assert result == {"Key": "Val"}

    def test_empty_input(self):
        assert _normalize_event_data({}) == {}
        assert _normalize_event_data(None) == {}

    def test_non_dict_input(self):
        assert _normalize_event_data("string") == {}
        assert _normalize_event_data(42) == {}


# ---------------------------------------------------------------------------
# get_event_data
# ---------------------------------------------------------------------------

class TestGetEventData:
    def test_event_data(self):
        data = {"Event": {"EventData": {"ServiceName": "TestSvc"}}}
        assert get_event_data(data)["ServiceName"] == "TestSvc"

    def test_user_data_fallback(self):
        data = {"Event": {"UserData": {"Key": "Value"}}}
        assert get_event_data(data)["Key"] == "Value"

    def test_event_data_takes_precedence(self):
        data = {
            "Event": {
                "EventData": {"Source": "ED"},
                "UserData": {"Source": "UD"},
            }
        }
        assert get_event_data(data)["Source"] == "ED"

    def test_neither_present(self):
        assert get_event_data({"Event": {}}) == {}
        assert get_event_data({}) == {}


# ---------------------------------------------------------------------------
# pid_hex_variants
# ---------------------------------------------------------------------------

class TestPidHexVariants:
    def test_known_pid(self):
        variants = pid_hex_variants(1052)
        assert "1052" in variants
        assert "0x41c" in variants
        assert "0x041c" in variants
        assert "0x0000041c" in variants

    def test_pid_zero(self):
        variants = pid_hex_variants(0)
        assert "0" in variants
        assert "0x0" in variants

    def test_large_pid(self):
        variants = pid_hex_variants(3992)
        assert "3992" in variants
        assert "0xf98" in variants


# ---------------------------------------------------------------------------
# _pid_in_fields
# ---------------------------------------------------------------------------

class TestPidInFields:
    def test_match_newprocessid(self):
        evdata = {"NewProcessId": "0x41c"}
        variants = pid_hex_variants(1052)
        assert _pid_in_fields(evdata, variants) is True

    def test_match_decimal(self):
        evdata = {"ProcessId": "1052"}
        variants = pid_hex_variants(1052)
        assert _pid_in_fields(evdata, variants) is True

    def test_no_match(self):
        evdata = {"NewProcessId": "0xdead"}
        variants = pid_hex_variants(1052)
        assert _pid_in_fields(evdata, variants) is False

    def test_non_pid_field_ignored(self):
        evdata = {"SomeOtherField": "0x41c"}
        variants = pid_hex_variants(1052)
        assert _pid_in_fields(evdata, variants) is False

    def test_empty_evdata(self):
        assert _pid_in_fields({}, {"1052"}) is False
        assert _pid_in_fields(None, {"1052"}) is False


# ---------------------------------------------------------------------------
# SECURITY_EVENTS constant
# ---------------------------------------------------------------------------

class TestSecurityEvents:
    def test_critical_events_present(self):
        """Ensure the most important security event IDs are tracked."""
        assert 4688 in SECURITY_EVENTS  # Process Created
        assert 7045 in SECURITY_EVENTS  # Service Installed
        assert 1102 in SECURITY_EVENTS  # Audit Log Cleared
        assert 4624 in SECURITY_EVENTS  # Logon Success
        assert 4625 in SECURITY_EVENTS  # Logon Failure

    def test_keys_are_ints_and_descriptions_are_nonempty_strings(self):
        for eid, desc in SECURITY_EVENTS.items():
            assert isinstance(eid, int), f"Key {eid} should be int"
            assert isinstance(desc, str), f"Value for {eid} should be str"
            assert len(desc) > 0, f"Description for {eid} should not be empty"
