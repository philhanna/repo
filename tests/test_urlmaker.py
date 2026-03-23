"""Tests for URL maker behavior."""

from repo_py.urlmaker import URLBuildError, URLRequest, build_url_from_parts, swap_prefix


def test_urlrequest_defaults() -> None:
    request = URLRequest()
    assert request.path == "."
    assert request.issue_flag is False
    assert request.issue_number == 0


def test_swap_prefix() -> None:
    have = swap_prefix("git@github.com:philhanna/repo", "git@github.com:", "https://github.com/")
    assert have == "https://github.com/philhanna/repo"


def test_build_url_trims_git_suffix_and_maps_prefix() -> None:
    request = URLRequest(path=".")
    prefix_map = {"git@github.com:": "https://github.com/"}
    have = build_url_from_parts(
        request,
        "git@github.com:philhanna/repo.git",
        "main",
        prefix_map,
    )
    assert have == "https://github.com/philhanna/repo"


def test_build_url_issue_flag_uses_branch_issue() -> None:
    request = URLRequest(issue_flag=True, issue_number=0, path=".")
    prefix_map = {"git@github.com:": "https://github.com/"}
    have = build_url_from_parts(
        request,
        "git@github.com:philhanna/repo.git",
        "defect#35-rename",
        prefix_map,
    )
    assert have == "https://github.com/philhanna/repo/issues/35"


def test_build_url_issue_flag_prefers_explicit_issue() -> None:
    request = URLRequest(issue_flag=True, issue_number=7, path=".")
    prefix_map = {"git@github.com:": "https://github.com/"}
    have = build_url_from_parts(
        request,
        "git@github.com:philhanna/repo",
        "defect#35-rename",
        prefix_map,
    )
    assert have == "https://github.com/philhanna/repo/issues/7"


def test_build_url_issue_flag_without_number_routes_to_issues() -> None:
    request = URLRequest(issue_flag=True, issue_number=0, path=".")
    prefix_map = {"git@github.com:": "https://github.com/"}
    have = build_url_from_parts(
        request,
        "git@github.com:philhanna/repo",
        "main",
        prefix_map,
    )
    assert have == "https://github.com/philhanna/repo/issues"


def test_build_url_raises_on_unsupported_prefix() -> None:
    request = URLRequest(path=".")
    try:
        build_url_from_parts(
            request,
            "ssh://example.com/philhanna/repo",
            "main",
            {"git@github.com:": "https://github.com/"},
        )
    except URLBuildError as exc:
        assert "Unsupported url type" in str(exc)
    else:
        raise AssertionError("Expected URLBuildError")
