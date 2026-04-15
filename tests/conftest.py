"""Shared fixtures for Claude-MKII tests."""

import os
import sys
import tempfile

import pytest

# Ensure the project-level "tools" directory is on sys.path so tests can import from it.
TOOLS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tools"))
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)

@pytest.fixture
def tmp_dir():
    """Provide a temporary directory that is cleaned up after the test."""
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture
def sample_text_file(tmp_dir):
    """Create a simple text file and return its path."""
    path = os.path.join(tmp_dir, "sample.md")
    with open(path, "w") as f:
        f.write("# Title\n\nSome content here.\nAnother line.\n")
    return path
