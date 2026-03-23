"""Placeholder tests for URL maker module scaffolding."""

from repo_py.urlmaker import URLRequest


def test_urlrequest_defaults() -> None:
    request = URLRequest()
    assert request.path == "."
    assert request.issue_flag is False
    assert request.issue_number == 0
