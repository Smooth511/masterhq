"""Tests for tools/safe_read.py — the attack-pattern scanner."""

import os

from safe_read import (
    MAX_CHARS_PER_LINE,
    MAX_CONSECUTIVE_BLANKS,
    MAX_FILE_SIZE_TEXT,
    ScanResult,
    is_binary,
    safe_read,
    scan_directory,
    scan_file,
)


# ---------------------------------------------------------------------------
# is_binary
# ---------------------------------------------------------------------------

class TestIsBinary:
    def test_binary_extension(self, tmp_dir):
        path = os.path.join(tmp_dir, "image.png")
        with open(path, "wb") as f:
            f.write(b"\x89PNG\r\n")
        assert is_binary(path) is True

    def test_text_file(self, sample_text_file):
        assert is_binary(sample_text_file) is False

    def test_null_bytes_in_content(self, tmp_dir):
        path = os.path.join(tmp_dir, "data.txt")
        with open(path, "wb") as f:
            f.write(b"hello\x00world")
        assert is_binary(path) is True


# ---------------------------------------------------------------------------
# scan_file — clean files
# ---------------------------------------------------------------------------

class TestScanFileClean:
    def test_clean_file_is_safe(self, sample_text_file):
        result = scan_file(sample_text_file)
        assert result.safe is True
        assert result.total_lines == 4
        assert len(result.alerts) == 0

    def test_binary_file_skipped(self, tmp_dir):
        path = os.path.join(tmp_dir, "photo.jpg")
        with open(path, "wb") as f:
            f.write(b"\xff\xd8\xff\xe0" + b"\x00" * 100)
        result = scan_file(path)
        assert result.total_lines == 0
        assert any("Binary" in a["message"] for a in result.alerts)

    def test_nonexistent_file(self, tmp_dir):
        result = scan_file(os.path.join(tmp_dir, "nope.txt"))
        assert result.safe is False  # can't read = flagged


# ---------------------------------------------------------------------------
# scan_file — attack patterns
# ---------------------------------------------------------------------------

class TestScanFileAttackPatterns:
    def test_mega_line_flagged(self, tmp_dir):
        """Lines over MAX_CHARS_PER_LINE should trigger CRITICAL alert."""
        path = os.path.join(tmp_dir, "megastr.txt")
        with open(path, "w") as f:
            f.write("A" * (MAX_CHARS_PER_LINE + 1) + "\n")
        result = scan_file(path)
        assert result.safe is False
        crits = [a for a in result.alerts if a["severity"] == "CRITICAL"]
        assert len(crits) >= 1
        assert result.max_line_length > MAX_CHARS_PER_LINE

    def test_whitespace_bomb_flagged(self, tmp_dir):
        """Excessive consecutive blank lines should trigger HIGH alert."""
        path = os.path.join(tmp_dir, "whitespace.txt")
        with open(path, "w") as f:
            f.write("start\n")
            f.write("\n" * (MAX_CONSECUTIVE_BLANKS + 10))
            f.write("end\n")
        result = scan_file(path)
        assert result.safe is False
        highs = [a for a in result.alerts if a["severity"] == "HIGH"]
        assert len(highs) >= 1

    def test_zero_width_chars_flagged(self, tmp_dir):
        """Zero-width unicode characters should trigger CRITICAL alert."""
        path = os.path.join(tmp_dir, "steganography.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write("normal text \u200b hidden \u200b data\n")
        result = scan_file(path)
        assert result.safe is False
        assert result.zero_width_count >= 2
        crits = [a for a in result.alerts if a["severity"] == "CRITICAL"]
        assert len(crits) >= 1

    def test_control_chars_flagged(self, tmp_dir):
        """Control characters (non tab/LF/CR) should trigger HIGH alert."""
        path = os.path.join(tmp_dir, "ctrl.txt")
        with open(path, "w") as f:
            f.write("hello\x01world\x02\n")
        result = scan_file(path)
        assert result.safe is False
        assert result.control_char_count >= 2

    def test_oversized_file_flagged(self, tmp_dir):
        """Files over MAX_FILE_SIZE_TEXT should get a HIGH alert."""
        path = os.path.join(tmp_dir, "huge.txt")
        with open(path, "w") as f:
            f.write("x" * (MAX_FILE_SIZE_TEXT + 1) + "\n")
        result = scan_file(path)
        highs = [a for a in result.alerts if a["severity"] == "HIGH"]
        assert any("exceeds" in a["message"] for a in highs)


# ---------------------------------------------------------------------------
# safe_read
# ---------------------------------------------------------------------------

class TestSafeRead:
    def test_clean_file_returned_verbatim(self, sample_text_file):
        content = safe_read(sample_text_file)
        assert "# Title" in content
        assert "Some content" in content

    def test_mega_line_truncated(self, tmp_dir):
        path = os.path.join(tmp_dir, "mega.txt")
        with open(path, "w") as f:
            f.write("B" * (MAX_CHARS_PER_LINE + 500) + "\n")
        content = safe_read(path)
        assert "TRUNCATED" in content
        assert "SAFE READ" in content

    def test_binary_file_rejected(self, tmp_dir):
        path = os.path.join(tmp_dir, "bin.exe")
        with open(path, "wb") as f:
            f.write(b"\x00" * 200)
        content = safe_read(path)
        assert "BINARY FILE" in content


# ---------------------------------------------------------------------------
# scan_directory
# ---------------------------------------------------------------------------

class TestScanDirectory:
    def test_scans_all_files(self, tmp_dir):
        for name in ["a.txt", "b.md", "c.py"]:
            with open(os.path.join(tmp_dir, name), "w") as f:
                f.write("content\n")
        results, flagged = scan_directory(tmp_dir)
        assert len(results) == 3
        assert len(flagged) == 0

    def test_flags_bad_files(self, tmp_dir):
        # One clean, one with zero-width chars
        with open(os.path.join(tmp_dir, "clean.txt"), "w") as f:
            f.write("normal\n")
        with open(os.path.join(tmp_dir, "bad.txt"), "w", encoding="utf-8") as f:
            f.write("hidden \u200b data\n")
        results, flagged = scan_directory(tmp_dir)
        assert len(results) == 2
        assert len(flagged) == 1
        assert "bad.txt" in flagged[0].filepath


# ---------------------------------------------------------------------------
# ScanResult
# ---------------------------------------------------------------------------

class TestScanResult:
    def test_str_clean(self):
        r = ScanResult("/tmp/test.txt")
        r.total_lines = 5
        r.file_size = 100
        output = str(r)
        assert "CLEAN" in output

    def test_str_flagged(self):
        r = ScanResult("/tmp/test.txt")
        r.total_lines = 5
        r.file_size = 100
        r.add_alert("CRITICAL", "test alert", 1)
        output = str(r)
        assert "FLAGGED" in output
        assert "test alert" in output
