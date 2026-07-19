"""Tests for CLI parsing behavior."""

import pytest

from repo_py.cli import parse_command_line, parse_issue_number


@pytest.mark.parametrize(
    ("value", "want"),
    [
        ("", 0),
        ("bogus", 0),
        ("3", 3),
        ("35", 35),
        ("#35", 35),
        ("issue#17", 17),
        ("defect#35-rename", 35),
        ("1 2 3", 1),
    ],
)
def test_parse_issue_number(value: str, want: int) -> None:
    assert parse_issue_number(value) == want


@pytest.mark.parametrize("option", ["-a", "--actions"])
def test_parse_actions_flag(option: str) -> None:
    command = parse_command_line([option])

    assert command.actions_flag is True
    assert command.issue_flag is False
