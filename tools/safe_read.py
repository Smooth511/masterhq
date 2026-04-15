#!/usr/bin/env python3
"""
mk2-phantom Safe Reading Protocol
===================================
Scans repository files for attack patterns that crash AI agents:
- Whitespace bombs (1000+ blank lines hiding data)
- Zero-linebreak megastrings (data hidden in single lines)
- Binary injection in text files
- Null bytes / control characters
- Zero-width unicode steganography
- Excessive line lengths that cause context overflow

Hard limit: 5000 chars per line. Anything over = auto-flag + safe truncation.
This prevents the 286k read / insta-crash pattern.

Usage:
    python tools/safe_read.py [path]           # Scan file or directory
    python tools/safe_read.py --scan-repo      # Full repo scan
    python tools/safe_read.py --read FILE      # Safe-read a file with protections
"""

import os
import sys
import re
from pathlib import Path

# === HARD LIMITS ===
MAX_CHARS_PER_LINE = 5000       # Auto-flag if exceeded
MAX_CONSECUTIVE_BLANKS = 50     # Whitespace bomb threshold
MAX_FILE_SIZE_TEXT = 2_000_000  # 2MB for text files - anything over = chunked read
ZERO_WIDTH_CHARS = {0x200B, 0x200C, 0x200D, 0xFEFF, 0x2060, 0x00AD, 0x2061, 0x2062, 0x2063, 0x2064}
BINARY_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.evtx', '.exe', '.dll', '.bin', '.zip', '.gz', '.tar'}

class ScanResult:
    def __init__(self, filepath):
        self.filepath = filepath
        self.alerts = []
        self.safe = True
        self.max_line_length = 0
        self.max_consecutive_blanks = 0
        self.zero_width_count = 0
        self.control_char_count = 0
        self.null_byte_count = 0
        self.total_lines = 0
        self.file_size = 0

    def add_alert(self, severity, message, line_num=None):
        self.alerts.append({
            'severity': severity,
            'message': message,
            'line': line_num
        })
        if severity in ('CRITICAL', 'HIGH'):
            self.safe = False

    def __str__(self):
        status = "✅ CLEAN" if self.safe else "⚠️  FLAGGED"
        lines = [f"{status} {self.filepath} ({self.file_size:,} bytes, {self.total_lines} lines)"]
        if self.max_line_length > MAX_CHARS_PER_LINE:
            lines.append(f"  MAX LINE: {self.max_line_length:,} chars (limit: {MAX_CHARS_PER_LINE})")
        for alert in self.alerts:
            prefix = "🔴" if alert['severity'] == 'CRITICAL' else "🟡" if alert['severity'] == 'HIGH' else "ℹ️ "
            loc = f" [line {alert['line']}]" if alert['line'] else ""
            lines.append(f"  {prefix} {alert['severity']}: {alert['message']}{loc}")
        return '\n'.join(lines)


def is_binary(filepath):
    """Check if file is binary by extension or content."""
    if Path(filepath).suffix.lower() in BINARY_EXTENSIONS:
        return True
    try:
        with open(filepath, 'rb') as f:
            chunk = f.read(8192)
            if b'\x00' in chunk:
                return True
    except (IOError, PermissionError):
        return True
    return False


def scan_file(filepath):
    """Scan a single file for attack patterns."""
    result = ScanResult(filepath)

    try:
        result.file_size = os.path.getsize(filepath)
    except OSError:
        result.add_alert('HIGH', 'Cannot read file size')
        return result

    # Skip binary files
    if is_binary(filepath):
        result.add_alert('INFO', f'Binary file skipped ({result.file_size:,} bytes)')
        result.total_lines = 0
        return result

    # Size check
    if result.file_size > MAX_FILE_SIZE_TEXT:
        result.add_alert('HIGH', f'File exceeds {MAX_FILE_SIZE_TEXT:,} byte text limit ({result.file_size:,} bytes) - chunked read required')

    try:
        with open(filepath, 'r', errors='replace') as f:
            consecutive_blanks = 0
            line_num = 0

            for line in f:
                line_num += 1
                line_len = len(line.rstrip('\n\r'))

                # Track max line length
                if line_len > result.max_line_length:
                    result.max_line_length = line_len

                # === CHECK 1: Mega-line (agent killer) ===
                if line_len > MAX_CHARS_PER_LINE:
                    result.add_alert('CRITICAL',
                        f'Line exceeds {MAX_CHARS_PER_LINE} char limit: {line_len:,} chars. '
                        f'AGENT CRASH RISK. First 100 chars: {line[:100]!r}',
                        line_num)

                # === CHECK 2: Whitespace bomb ===
                if line.strip() == '':
                    consecutive_blanks += 1
                    if consecutive_blanks > result.max_consecutive_blanks:
                        result.max_consecutive_blanks = consecutive_blanks
                else:
                    if consecutive_blanks > MAX_CONSECUTIVE_BLANKS:
                        result.add_alert('HIGH',
                            f'{consecutive_blanks} consecutive blank lines detected '
                            f'(possible whitespace bomb / hidden data)',
                            line_num - consecutive_blanks)
                    consecutive_blanks = 0

                # === CHECK 3: Zero-width unicode ===
                for char in line:
                    if ord(char) in ZERO_WIDTH_CHARS:
                        result.zero_width_count += 1

                # === CHECK 4: Control characters ===
                for char in line:
                    cp = ord(char)
                    if cp < 32 and cp not in (9, 10, 13):  # Allow tab, LF, CR
                        result.control_char_count += 1

            result.total_lines = line_num

            # Final blank line check
            if consecutive_blanks > MAX_CONSECUTIVE_BLANKS:
                result.add_alert('HIGH',
                    f'{consecutive_blanks} trailing blank lines (possible whitespace bomb)',
                    line_num - consecutive_blanks)

            # Report zero-width chars
            if result.zero_width_count > 0:
                result.add_alert('CRITICAL',
                    f'{result.zero_width_count} zero-width unicode characters detected '
                    f'(possible steganography / hidden data)')

            # Report control chars
            if result.control_char_count > 0:
                result.add_alert('HIGH',
                    f'{result.control_char_count} control characters detected '
                    f'(possible binary injection)')

    except Exception as e:
        result.add_alert('HIGH', f'Read error: {e}')

    return result


def safe_read(filepath, max_chars_per_line=MAX_CHARS_PER_LINE):
    """
    Safe-read a file with hard limits.
    Returns sanitized content that won't crash an agent.
    """
    if is_binary(filepath):
        return f"[BINARY FILE - {os.path.getsize(filepath):,} bytes - not safe to read as text]"

    lines = []
    truncated_count = 0

    try:
        with open(filepath, 'r', errors='replace') as f:
            for i, line in enumerate(f, 1):
                clean = line.rstrip('\n\r')
                if len(clean) > max_chars_per_line:
                    truncated_count += 1
                    lines.append(
                        f"[LINE {i} TRUNCATED: {len(clean):,} chars -> {max_chars_per_line}] "
                        f"{clean[:max_chars_per_line]}"
                    )
                else:
                    lines.append(clean)
    except Exception as e:
        return f"[READ ERROR: {e}]"

    result = '\n'.join(lines)
    if truncated_count > 0:
        result = (
            f"⚠️ SAFE READ: {truncated_count} lines truncated at {max_chars_per_line} chars\n"
            f"{'='*60}\n"
            f"{result}"
        )
    return result


def scan_directory(dirpath, skip_git=True):
    """Scan all files in a directory tree."""
    results = []
    flagged = []

    for root, dirs, files in os.walk(dirpath):
        if skip_git and '.git' in root.split(os.sep):
            continue
        for filename in sorted(files):
            filepath = os.path.join(root, filename)
            result = scan_file(filepath)
            results.append(result)
            if not result.safe:
                flagged.append(result)

    return results, flagged


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    if sys.argv[1] == '--scan-repo':
        target = '.' if len(sys.argv) < 3 else sys.argv[2]
        print(f"🔍 Scanning {os.path.abspath(target)}...\n")
        results, flagged = scan_directory(target)

        # Summary
        print(f"\n{'='*60}")
        print(f"SCAN COMPLETE: {len(results)} files scanned")
        print(f"{'='*60}")

        if flagged:
            print(f"\n⚠️  {len(flagged)} FILES FLAGGED:\n")
            for r in flagged:
                print(r)
                print()
        else:
            print("\n✅ ALL FILES CLEAN - No attack patterns detected")

        # Stats
        max_line_file = max(results, key=lambda r: r.max_line_length) if results else None
        if max_line_file and max_line_file.max_line_length > 0:
            print(f"\nLongest line in repo: {max_line_file.max_line_length:,} chars "
                  f"in {max_line_file.filepath}")

    elif sys.argv[1] == '--read':
        if len(sys.argv) < 3:
            print("Usage: safe_read.py --read FILE")
            sys.exit(1)
        print(safe_read(sys.argv[2]))

    else:
        # Scan specific file
        filepath = sys.argv[1]
        if os.path.isdir(filepath):
            results, flagged = scan_directory(filepath)
            for r in results:
                print(r)
        else:
            result = scan_file(filepath)
            print(result)


if __name__ == '__main__':
    main()
