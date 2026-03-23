"""Tests for CLI parsing scaffolding."""

from repo_py.cli import parse_issue_number


def test_parse_issue_number_smoke() -> None:
    assert parse_issue_number("#35") == 35
