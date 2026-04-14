#!/usr/bin/env python3
"""
EVTX Parser - ClaudeMKII Security Investigation Tool
Parses Windows Event Log files (.evtx) to JSON for analysis.

Usage:
    python parse_evtx.py <file.evtx> [output.json]
    python parse_evtx.py <file.evtx> --hunt-pids 1052 3992
    python parse_evtx.py <file.evtx> --event-ids 4688 7045
    python parse_evtx.py <file.evtx> --all

Install:
    pip install evtx
"""

import json
import sys
import argparse
from pathlib import Path
from collections import Counter

try:
    from evtx import PyEvtxParser
except ImportError:
    print("ERROR: evtx library not installed. Run: pip install evtx", file=sys.stderr)
    sys.exit(1)

# Security-relevant event IDs with descriptions
SECURITY_EVENTS = {
    # Process activity
    4688: "Process Created",
    4689: "Process Terminated",
    # Service activity
    7045: "Service Installed",
    7040: "Service Start Type Changed",
    # Audit log
    1102: "Audit Log Cleared",
    1100: "Event Logging Shutdown",
    1101: "Audit Events Dropped",
    # Scheduled tasks
    4698: "Scheduled Task Created",
    4699: "Scheduled Task Deleted",
    4700: "Scheduled Task Enabled",
    4701: "Scheduled Task Disabled",
    # Logon
    4624: "Logon Success",
    4625: "Logon Failure",
    4634: "Logoff",
    4647: "User Initiated Logoff",
    # Credential / privilege
    4672: "Special Privileges Assigned",
    4673: "Privileged Service Called",
    5379: "Credential Manager Read",
    # Network filter (Windows Firewall)
    5156: "Network Connection Allowed",
    5157: "Network Connection Blocked",
    5152: "Packet Dropped",
    5158: "Bind Allowed",
    # Misc security
    4697: "Service Installed (Security log)",
    4902: "Per-user Audit Policy Table Created",
    4907: "Audit Policy Changed",
}


def get_event_id(data: dict) -> int:
    """Extract integer event ID from a parsed EVTX record.

    Some event logs store EventID as a plain int, others as a dict with a
    '#text' key (e.g. {'#text': '4688', 'Qualifiers': '0'}). Returns 0 if
    the value cannot be parsed.
    """
    eid = data.get("Event", {}).get("System", {}).get("EventID")
    if isinstance(eid, dict):
        eid = eid.get("#text")
    try:
        return int(eid)
    except (TypeError, ValueError):
        return 0


def _normalize_event_data(evdata) -> dict:
    """Normalize EVTX EventData/UserData into a flat dict.
    
    EVTX payloads can appear in two forms:
    1. Flat dict: {"NewProcessId": "0x41c", "NewProcessName": "cmd.exe"}
    2. Data array: {"Data": [{"@Name": "NewProcessId", "#text": "0x41c"}, ...]}
    
    This normalizes both forms to a flat dict for consistent field access.
    """
    if not evdata:
        return {}
    if not isinstance(evdata, dict):
        return {}
    
    # Check for Data array form (legacy)
    data_list = evdata.get("Data")
    if isinstance(data_list, list):
        flat = {}
        for item in data_list:
            if isinstance(item, dict):
                name = item.get("@Name")
                text = item.get("#text", "")
                if name:
                    flat[name] = text
            elif isinstance(item, str):
                # Skip plain string Data entries (occurs in some telemetry/diagnostic events
                # where the full payload is a single string, not structured key-value pairs)
                continue
        return flat
    
    # Already flat dict form
    return evdata


def get_event_data(data: dict) -> dict:
    """Extract event payload from a parsed EVTX record.

    Tries EventData first (most security events), falls back to UserData
    (application/operational events), and returns an empty dict if neither
    field is present. Normalizes Data array form to flat dict.
    """
    event = data.get("Event", {})
    evdata = event.get("EventData") or event.get("UserData") or {}
    return _normalize_event_data(evdata)


def pid_hex_variants(pid_int: int) -> set:
    """Return hex and decimal variants of a PID for exact field matching.
    
    Windows PIDs in EVTX can appear as:
    - Decimal: 1052, 3992
    - Hex with 0x prefix: 0x41c, 0xf98
    - Zero-padded hex (4-digit): 0x041c, 0x0f98
    - Zero-padded hex (8-digit): 0x0000041c, 0x00000f98
    """
    h = format(pid_int, "x")
    h_padded_4 = format(pid_int, "04x")
    h_padded_8 = format(pid_int, "08x")
    return {f"0x{h}", f"0x{h_padded_4}", f"0x{h_padded_8}", str(pid_int)}


_PID_FIELD_NAMES = {
    "newprocessid", "processid", "subjectprocessid", "callerprocessid",
    "targetprocessid", "parentprocessid", "processidentifier",
}


def _pid_in_fields(evdata: dict, variants: set) -> bool:
    """Check if any PID-related field in evdata exactly matches one of the variants."""
    if not isinstance(evdata, dict):
        return False
    for key, val in evdata.items():
        if key.lower() in _PID_FIELD_NAMES:
            if str(val).lower() in {v.lower() for v in variants}:
                return True
    return False


def parse_evtx(
    filepath: str,
    filter_ids: set = None,
    hunt_pids: list = None,
    search_strings: list = None,
) -> dict:
    """
    Parse an EVTX file and return structured results.

    Args:
        filepath: Path to .evtx file
        filter_ids: Set of event IDs to include (None = all)
        hunt_pids: List of PIDs (int) to search for in process events
        search_strings: List of strings to search for in raw event data

    Returns:
        dict with keys: events, summary, pid_findings, service_installs
    """
    filepath = str(filepath)
    pid_hex_sets = {}
    if hunt_pids:
        for pid in hunt_pids:
            pid_hex_sets[pid] = pid_hex_variants(pid)

    events = []
    all_event_ids = Counter()
    pid_findings = {pid: [] for pid in (hunt_pids or [])}
    service_installs = []
    process_creations = []

    parser = PyEvtxParser(filepath)

    for record in parser.records_json():
        try:
            raw = record.get("data", "")
            timestamp = record.get("timestamp", "")
            if not raw:
                continue
            data = json.loads(raw)
        except (json.JSONDecodeError, KeyError, TypeError):
            # Skip malformed records - missing keys, bad JSON, or unexpected types
            continue
            
        eid = get_event_id(data)
        all_event_ids[eid] += 1

        include = False

        # Filter by event ID
        if filter_ids is not None:
            if eid in filter_ids:
                include = True
        else:
            include = True

        # Check for PID matches - scan known PID-carrying fields for exact value match
        pid_hit = None
        if hunt_pids:
            evdata_check = get_event_data(data)
            for pid, variants in pid_hex_sets.items():
                if _pid_in_fields(evdata_check, variants):
                    pid_hit = pid
                    include = True
                    break

        # Check for search strings
        if search_strings:
            if any(s.lower() in raw.lower() for s in search_strings):
                include = True

        if not include:
            continue

        evdata = get_event_data(data)
        entry = {
            "timestamp": timestamp,
            "event_id": eid,
            "event_name": SECURITY_EVENTS.get(eid, f"Event {eid}"),
            "data": evdata,
        }

        events.append(entry)

        # Track PID findings
        if pid_hit is not None:
            pid_findings[pid_hit].append(entry)

        # Capture service installs for summary
        if eid == 7045:
            service_installs.append({
                "timestamp": timestamp,
                "service_name": evdata.get("ServiceName", ""),
                "image_path": evdata.get("ImagePath", ""),
                "service_type": evdata.get("ServiceType", ""),
                "start_type": evdata.get("StartType", ""),
                "account": evdata.get("AccountName", ""),
            })

        # Capture process creations for summary
        if eid == 4688:
            process_creations.append({
                "timestamp": timestamp,
                "pid": evdata.get("NewProcessId", ""),
                "process": evdata.get("NewProcessName", ""),
                "parent": evdata.get("ParentProcessName", ""),
                "cmdline": evdata.get("CommandLine", ""),
                "user": evdata.get("SubjectUserName", ""),
            })

    return {
        "source_file": filepath,
        "total_records": sum(all_event_ids.values()),
        "event_id_distribution": dict(
            sorted(all_event_ids.items(), key=lambda x: -x[1])
        ),
        "matched_events": len(events),
        "events": events,
        "pid_findings": {
            str(k): v for k, v in pid_findings.items()
        },
        "service_installs": service_installs,
        "process_creations": process_creations,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Parse Windows EVTX event logs to JSON for security analysis"
    )
    parser.add_argument("evtx_file", help="Path to the .evtx file")
    parser.add_argument("output", nargs="?", help="Output JSON file (default: stdout)")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Export all events (default: security events only)",
    )
    parser.add_argument(
        "--event-ids",
        nargs="+",
        type=int,
        metavar="ID",
        help="Filter to specific event IDs (e.g. 4688 7045)",
    )
    parser.add_argument(
        "--hunt-pids",
        nargs="+",
        type=int,
        metavar="PID",
        help="Hunt for specific PIDs across all events (e.g. 1052 3992)",
    )
    parser.add_argument(
        "--search",
        nargs="+",
        metavar="STRING",
        help="Search for strings in event data (case-insensitive)",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Print summary stats only, no full event dump",
    )

    args = parser.parse_args()

    evtx_path = Path(args.evtx_file)
    if not evtx_path.exists():
        print(f"ERROR: File not found: {evtx_path}", file=sys.stderr)
        sys.exit(1)

    # Determine event ID filter
    if args.all:
        filter_ids = None
    elif args.event_ids:
        filter_ids = set(args.event_ids)
    else:
        filter_ids = set(SECURITY_EVENTS.keys())

    print(f"Parsing: {evtx_path}", file=sys.stderr)
    if args.hunt_pids:
        print(f"Hunting PIDs: {args.hunt_pids}", file=sys.stderr)
    if filter_ids:
        print(f"Filtering to event IDs: {sorted(filter_ids)}", file=sys.stderr)

    results = parse_evtx(
        filepath=str(evtx_path),
        filter_ids=filter_ids,
        hunt_pids=args.hunt_pids,
        search_strings=args.search,
    )

    if args.summary_only:
        # Summary mode: counts and top-5 samples, not full lists
        summary = {
            "source_file": results["source_file"],
            "total_records": results["total_records"],
            "matched_events": results["matched_events"],
            "service_installs_count": len(results["service_installs"]),
            "process_creations_count": len(results["process_creations"]),
            "top_event_ids": dict(
                list(results["event_id_distribution"].items())[:20]
            ),
            # Top 5 samples only for quick stats
            "service_installs_sample": results["service_installs"][:5],
            "process_creations_sample": results["process_creations"][:5],
            # PID findings: counts and samples
            "pid_findings": {
                pid: {
                    "count": len(events),
                    "sample": events[:3]
                }
                for pid, events in results["pid_findings"].items()
            },
        }
        output_data = summary
    else:
        output_data = results

    output_json = json.dumps(output_data, indent=2, default=str)

    if args.output:
        out_path = Path(args.output)
        out_path.write_text(output_json, encoding="utf-8")
        print(
            f"Wrote {results['matched_events']} matched events to {out_path}",
            file=sys.stderr,
        )
        print(
            f"Total records in file: {results['total_records']}",
            file=sys.stderr,
        )
        if args.hunt_pids:
            for pid, findings in results["pid_findings"].items():
                print(
                    f"PID {pid} findings: {len(findings)} events", file=sys.stderr
                )
    else:
        print(output_json)


if __name__ == "__main__":
    main()
