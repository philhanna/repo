"""Tests for domain URL-building services."""

from repo_py.domain.errors import URLBuildError
from repo_py.domain.models import GiteaConfig, URLRequest
from repo_py.domain.services import build_url_from_parts, normalize_remote_url


def test_urlrequest_defaults() -> None:
    request = URLRequest()
    assert request.path == "."
    assert request.actions_flag is False
    assert request.issue_flag is False
    assert request.issue_number == 0


def test_normalize_remote_url_scp_like() -> None:
    have = normalize_remote_url("git@github.com:philhanna/repo")
    assert have == "https://github.com/philhanna/repo"


def test_normalize_remote_url_ssh_scheme() -> None:
    have = normalize_remote_url("ssh://git@github.com/philhanna/repo")
    assert have == "https://github.com/philhanna/repo"


def test_normalize_remote_url_ssh_scheme_with_port() -> None:
    have = normalize_remote_url("ssh://git@example.com:2222/philhanna/repo")
    assert have == "https://example.com/philhanna/repo"


def test_normalize_remote_url_passes_through_https() -> None:
    have = normalize_remote_url("https://github.com/philhanna/repo")
    assert have == "https://github.com/philhanna/repo"


def test_normalize_remote_url_arbitrary_host() -> None:
    have = normalize_remote_url("git@gitea.example.com:group/project.git")
    assert have == "https://gitea.example.com/group/project"


def test_normalize_remote_url_scp_like_gitea_override() -> None:
    have = normalize_remote_url(
        "git@localhost:philhanna/repo.git",
        GiteaConfig(host="localhost", port=3000),
    )
    assert have == "http://localhost:3000/philhanna/repo"


def test_normalize_remote_url_ssh_scheme_gitea_override() -> None:
    have = normalize_remote_url(
        "ssh://git@localhost/philhanna/repo",
        GiteaConfig(host="localhost", port=3000),
    )
    assert have == "http://localhost:3000/philhanna/repo"


def test_normalize_remote_url_gitea_override_ignores_other_hosts() -> None:
    have = normalize_remote_url(
        "git@github.com:philhanna/repo.git",
        GiteaConfig(host="localhost", port=3000),
    )
    assert have == "https://github.com/philhanna/repo"


def test_normalize_remote_url_without_gitea_config_uses_https() -> None:
    have = normalize_remote_url("git@localhost:philhanna/repo.git")
    assert have == "https://localhost/philhanna/repo"


def test_normalize_remote_url_raises_on_unsupported_form() -> None:
    try:
        normalize_remote_url("not-a-valid-remote")
    except URLBuildError as exc:
        assert "Unsupported url type" in str(exc)
    else:
        raise AssertionError("Expected URLBuildError")


def test_build_url_trims_git_suffix_and_maps_prefix() -> None:
    request = URLRequest(path=".")
    have = build_url_from_parts(
        request,
        "git@github.com:philhanna/repo.git",
        "main",
    )
    assert have == "https://github.com/philhanna/repo"


def test_build_url_issue_flag_uses_branch_issue() -> None:
    request = URLRequest(issue_flag=True, issue_number=0, path=".")
    have = build_url_from_parts(
        request,
        "git@github.com:philhanna/repo.git",
        "defect#35-rename",
    )
    assert have == "https://github.com/philhanna/repo/issues/35"


def test_build_url_issue_flag_prefers_explicit_issue() -> None:
    request = URLRequest(issue_flag=True, issue_number=7, path=".")
    have = build_url_from_parts(
        request,
        "git@github.com:philhanna/repo",
        "defect#35-rename",
    )
    assert have == "https://github.com/philhanna/repo/issues/7"


def test_build_url_issue_flag_without_number_routes_to_issues() -> None:
    request = URLRequest(issue_flag=True, issue_number=0, path=".")
    have = build_url_from_parts(
        request,
        "git@github.com:philhanna/repo",
        "main",
    )
    assert have == "https://github.com/philhanna/repo/issues"


def test_build_url_actions_flag_routes_to_actions() -> None:
    request = URLRequest(actions_flag=True, path=".")
    have = build_url_from_parts(
        request,
        "git@github.com:philhanna/repo.git",
        "main",
    )
    assert have == "https://github.com/philhanna/repo/actions"


def test_build_url_raises_on_unsupported_prefix() -> None:
    request = URLRequest(path=".")
    try:
        build_url_from_parts(
            request,
            "not-a-valid-remote",
            "main",
        )
    except URLBuildError as exc:
        assert "Unsupported url type" in str(exc)
    else:
        raise AssertionError("Expected URLBuildError")
