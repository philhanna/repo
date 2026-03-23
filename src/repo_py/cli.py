"""Command-line argument parsing for the repo Python port."""

from __future__ import annotations

from dataclasses import dataclass
import argparse
import re


@dataclass(slots=True)
class CommandLine:
    issue_flag: bool = False
    issue_number: int = 0
    path: str = "."


def parse_issue_number(value: str) -> int:
    """Extract the first issue number from a string; return 0 if not found."""
    if not value:
        return 0
    match = re.search(r"#?(\d+)", value.upper())
    if not match:
        return 0
    return int(match.group(1))


def parse_command_line(argv: list[str] | None = None) -> CommandLine:
    """Parse CLI arguments into a typed command object."""
    parser = argparse.ArgumentParser(
        prog="repo",
        description="Launches a browser window for a page of the git remote repository.",
    )
    parser.add_argument(
        "issue",
        nargs="?",
        default="",
        help=(
            "Optional issue number. Accepts values like '35', '#35', "
            "'issue#35', or 'defect#35-rename'."
        ),
    )
    parser.add_argument(
        "-i",
        "--issue",
        action="store_true",
        dest="issue_flag",
        help="Display the main issues page. If the branch contains an issue number, use that.",
    )
    parser.add_argument(
        "-p",
        "--path",
        default=".",
        help='Path to local repository (Default=".")',
    )

    args = parser.parse_args(argv)
    return CommandLine(
        issue_flag=args.issue_flag,
        issue_number=parse_issue_number(args.issue),
        path=args.path,
    )
