#!/usr/bin/env python3
"""
Claude-MKII MCP Server

Implements the Model Context Protocol (stdio transport) for VS Code integration.
Exposes tools for reading project files, listing directories, searching content,
reading log/evidence directories, and summarising project structure.

Usage:
    python mcp-server/server.py

VS Code connects to this via the .vscode/mcp.json configuration.
"""

import json
import os
from datetime import datetime
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Project root is one level above this file (mcp-server/ -> repo root)
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).parent.parent.resolve()

# Directories that hold markdown documentation / logs
DOC_DIRS = ["core", "investigation", "evidence", "logs"]

# Tuneable limits
MAX_SEARCH_RESULTS = 200
SEPARATOR_LENGTH = 60

mcp = FastMCP("Claude-MKII")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_path(relative: str) -> Path:
    """Resolve a user-supplied relative path and ensure it stays inside the project."""
    target = (PROJECT_ROOT / relative).resolve()
    if not str(target).startswith(str(PROJECT_ROOT)):
        raise ValueError(f"Path '{relative}' escapes the project root.")
    return target


def _read_text(path: Path, max_bytes: int = 1_000_000) -> str:
    """Read a text file, truncating if it exceeds max_bytes."""
    size = path.stat().st_size
    with path.open("r", encoding="utf-8", errors="replace") as fh:
        content = fh.read(max_bytes)
    if size > max_bytes:
        content += f"\n\n[Truncated — file is {size} bytes, showed first {max_bytes}]"
    return content


# ---------------------------------------------------------------------------
# Tool: read_file
# ---------------------------------------------------------------------------

@mcp.tool()
def read_file(path: str) -> str:
    """Read a file from the project.

    Args:
        path: Path relative to the project root (e.g. 'README.md' or 'core/TROUBLESHOOTING.md').

    Returns:
        The text content of the file.
    """
    target = _safe_path(path)
    if not target.exists():
        return f"Error: '{path}' does not exist."
    if not target.is_file():
        return f"Error: '{path}' is a directory, not a file."
    try:
        return _read_text(target)
    except Exception as exc:
        return f"Error reading '{path}': {exc}"


# ---------------------------------------------------------------------------
# Tool: list_directory
# ---------------------------------------------------------------------------

@mcp.tool()
def list_directory(path: str = "") -> str:
    """List the contents of a directory in the project.

    Args:
        path: Path relative to the project root. Defaults to the project root.

    Returns:
        A formatted directory listing.
    """
    target = _safe_path(path) if path else PROJECT_ROOT
    if not target.exists():
        return f"Error: '{path}' does not exist."
    if not target.is_dir():
        return f"Error: '{path}' is a file, not a directory."

    lines = [f"Directory: {target.relative_to(PROJECT_ROOT) if path else '.'}", ""]
    entries = sorted(target.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
    for entry in entries:
        if entry.name.startswith("."):
            continue
        prefix = "📁 " if entry.is_dir() else "📄 "
        rel = entry.relative_to(PROJECT_ROOT)
        lines.append(f"{prefix}{rel}")

    return "\n".join(lines) if lines else "(empty directory)"


# ---------------------------------------------------------------------------
# Tool: search_files
# ---------------------------------------------------------------------------

@mcp.tool()
def search_files(query: str, directory: str = "", extensions: str = ".md,.txt,.py") -> str:
    """Search for text across project files.

    Args:
        query: The text string to search for (case-insensitive).
        directory: Subdirectory to limit the search to (defaults to entire project).
        extensions: Comma-separated list of file extensions to include (e.g. '.md,.py').

    Returns:
        Matching lines with file paths and line numbers.
    """
    search_root = _safe_path(directory) if directory else PROJECT_ROOT
    exts = {e.strip().lower() for e in extensions.split(",")}
    query_lower = query.lower()

    matches: list[str] = []
    for filepath in search_root.rglob("*"):
        if not filepath.is_file():
            continue
        if filepath.suffix.lower() not in exts:
            continue
        # Skip binary-looking files by trying a small read
        try:
            with filepath.open("r", encoding="utf-8", errors="replace") as fh:
                for lineno, line in enumerate(fh, start=1):
                    if query_lower in line.lower():
                        rel = filepath.relative_to(PROJECT_ROOT)
                        matches.append(f"{rel}:{lineno}: {line.rstrip()}")
                        if len(matches) >= MAX_SEARCH_RESULTS:
                            matches.append(f"... (truncated at {MAX_SEARCH_RESULTS} results)")
                            return "\n".join(matches)
        except Exception:
            continue

    if not matches:
        return f"No matches found for '{query}'."
    return "\n".join(matches)


# ---------------------------------------------------------------------------
# Tool: read_logs
# ---------------------------------------------------------------------------

@mcp.tool()
def read_logs(subdirectory: str = "", recent: bool = False) -> str:
    """Read markdown files from the project's log/documentation directories.

    Args:
        subdirectory: One of 'core', 'investigation', 'evidence', 'logs', or empty for all.
        recent: If True, only return the most recently modified file from each directory.

    Returns:
        Concatenated contents of the matching markdown files.
    """
    if subdirectory and subdirectory not in DOC_DIRS:
        return f"Error: subdirectory must be one of {DOC_DIRS} or empty."

    dirs = [PROJECT_ROOT / d for d in (DOC_DIRS if not subdirectory else [subdirectory])]

    results: list[str] = []
    for doc_dir in dirs:
        if not doc_dir.is_dir():
            continue
        md_files = sorted(
            [f for f in doc_dir.rglob("*.md") if f.is_file()],
            key=lambda f: f.stat().st_mtime,
            reverse=True,
        )
        if recent:
            md_files = md_files[:1]
        for md_file in md_files:
            rel = md_file.relative_to(PROJECT_ROOT)
            mtime = datetime.fromtimestamp(md_file.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            results.append(f"\n{'='*SEPARATOR_LENGTH}")
            results.append(f"FILE: {rel}  (modified {mtime})")
            results.append("="*SEPARATOR_LENGTH)
            results.append(_read_text(md_file, max_bytes=50_000))

    if not results:
        return "No markdown files found in the specified directories."
    return "\n".join(results)


# ---------------------------------------------------------------------------
# Tool: project_status
# ---------------------------------------------------------------------------

@mcp.tool()
def project_status() -> str:
    """Return a summary of the project structure and recent activity.

    Returns:
        A human-readable overview of the project.
    """
    lines = [
        f"# Claude-MKII Project Status",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Root: {PROJECT_ROOT}",
        "",
    ]

    # Top-level directory overview
    lines.append("## Directory structure")
    for item in sorted(PROJECT_ROOT.iterdir(), key=lambda p: (p.is_file(), p.name)):
        if item.name.startswith(".") or item.name in {"__pycache__", "node_modules"}:
            continue
        kind = "DIR " if item.is_dir() else "FILE"
        lines.append(f"  {kind}  {item.name}")

    lines.append("")
    lines.append("## Documentation directories")
    for dname in DOC_DIRS:
        d = PROJECT_ROOT / dname
        if not d.is_dir():
            lines.append(f"  {dname}: (not found)")
            continue
        md_files = list(d.rglob("*.md"))
        lines.append(f"  {dname}/: {len(md_files)} markdown file(s)")

    # Most recently modified files
    lines.append("")
    lines.append("## Recently modified files (top 10)")
    all_files = [
        f for f in PROJECT_ROOT.rglob("*")
        if f.is_file() and not any(part.startswith(".") for part in f.parts)
    ]
    all_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    for f in all_files[:10]:
        mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        rel = f.relative_to(PROJECT_ROOT)
        lines.append(f"  {mtime}  {rel}")

    # Tools available
    lines.append("")
    lines.append("## Available tools")
    tools_dir = PROJECT_ROOT / "tools"
    if tools_dir.is_dir():
        for t in sorted(tools_dir.iterdir()):
            if t.suffix == ".py":
                lines.append(f"  tools/{t.name}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="stdio")
