#!/usr/bin/env python3
"""
Claude-MKII CLI Tool (mk2)

Provides a command-line interface for common project operations.

Commands:
    status              Show project structure and recent activity.
    read <path>         Print a file from the project.
    search <query>      Search for text across project files.
    logs [--recent]     Read log/documentation directories.
    serve               Start the MCP server (stdio).

Usage:
    python cli/mk2_cli.py status
    python cli/mk2_cli.py read README.md
    python cli/mk2_cli.py search "rootkit"
    python cli/mk2_cli.py logs --recent
    python cli/mk2_cli.py serve
"""

import argparse
import subprocess
import sys
from pathlib import Path

# Project root is one level above this file (cli/ -> repo root)
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
MCP_SERVER = PROJECT_ROOT / "mcp-server" / "server.py"

# Make the mcp-server module importable
_MCP_SERVER_DIR = str(PROJECT_ROOT / "mcp-server")
if _MCP_SERVER_DIR not in sys.path:
    sys.path.insert(0, _MCP_SERVER_DIR)


# ---------------------------------------------------------------------------
# Helpers (thin wrappers that call the same logic as the MCP server)
# ---------------------------------------------------------------------------

def _safe_path(relative: str) -> Path:
    target = (PROJECT_ROOT / relative).resolve()
    if not str(target).startswith(str(PROJECT_ROOT)):
        print(f"Error: '{relative}' escapes the project root.", file=sys.stderr)
        sys.exit(1)
    return target


# ---------------------------------------------------------------------------
# Command implementations
# ---------------------------------------------------------------------------

def cmd_status(_args: argparse.Namespace) -> None:
    """Print a project overview."""
    # Import and call the MCP tool directly so logic stays DRY
    from server import project_status  # type: ignore[import]
    print(project_status())


def cmd_read(args: argparse.Namespace) -> None:
    """Print the contents of a file."""
    target = _safe_path(args.path)
    if not target.exists():
        print(f"Error: '{args.path}' does not exist.", file=sys.stderr)
        sys.exit(1)
    if not target.is_file():
        print(f"Error: '{args.path}' is a directory.", file=sys.stderr)
        sys.exit(1)
    try:
        print(target.read_text(encoding="utf-8", errors="replace"))
    except Exception as exc:
        print(f"Error reading '{args.path}': {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_search(args: argparse.Namespace) -> None:
    """Search for text across project files."""
    from server import search_files  # type: ignore[import]
    directory = getattr(args, "directory", "") or ""
    extensions = getattr(args, "extensions", ".md,.txt,.py") or ".md,.txt,.py"
    print(search_files(args.query, directory=directory, extensions=extensions))


def cmd_logs(args: argparse.Namespace) -> None:
    """Read log/documentation directories."""
    from server import read_logs  # type: ignore[import]
    subdir = getattr(args, "subdirectory", "") or ""
    recent = getattr(args, "recent", False)
    print(read_logs(subdirectory=subdir, recent=recent))


def cmd_serve(_args: argparse.Namespace) -> None:
    """Start the MCP server."""
    if not MCP_SERVER.exists():
        print(f"Error: MCP server not found at {MCP_SERVER}", file=sys.stderr)
        sys.exit(1)
    print(f"Starting MCP server: {MCP_SERVER}", file=sys.stderr)
    try:
        subprocess.run([sys.executable, str(MCP_SERVER)], check=True)
    except KeyboardInterrupt:
        print("\nMCP server stopped.", file=sys.stderr)


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mk2",
        description="Claude-MKII CLI — interact with the project from the command line.",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="<command>")

    # status
    subparsers.add_parser("status", help="Show project structure and recent activity.")

    # read
    read_p = subparsers.add_parser("read", help="Print a file from the project.")
    read_p.add_argument("path", help="Path relative to the project root.")

    # search
    search_p = subparsers.add_parser("search", help="Search for text across project files.")
    search_p.add_argument("query", help="Text to search for (case-insensitive).")
    search_p.add_argument(
        "--directory", "-d", default="",
        help="Limit search to this subdirectory.",
    )
    search_p.add_argument(
        "--extensions", "-e", default=".md,.txt,.py",
        help="Comma-separated file extensions to search (default: .md,.txt,.py).",
    )

    # logs
    logs_p = subparsers.add_parser("logs", help="Read log/documentation directories.")
    logs_p.add_argument(
        "subdirectory", nargs="?", default="",
        choices=["", "core", "investigation", "evidence", "logs"],
        help="Which directory to read (default: all).",
    )
    logs_p.add_argument(
        "--recent", action="store_true",
        help="Only show the most recently modified file in each directory.",
    )

    # serve
    subparsers.add_parser("serve", help="Start the MCP server (stdio transport).")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    dispatch = {
        "status": cmd_status,
        "read": cmd_read,
        "search": cmd_search,
        "logs": cmd_logs,
        "serve": cmd_serve,
    }

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    handler = dispatch.get(args.command)
    if handler is None:
        parser.print_help()
        sys.exit(1)

    handler(args)


if __name__ == "__main__":
    main()
