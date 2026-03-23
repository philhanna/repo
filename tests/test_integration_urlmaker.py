"""Integration-style tests for URL building against temporary git repositories."""

from __future__ import annotations

from pathlib import Path
import subprocess

import pytest

import repo_py.urlmaker as urlmaker
from repo_py.urlmaker import URLBuildError, URLRequest, build_url


def _git(repo_path: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo_path,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _init_repo_with_commit(repo_path: Path) -> None:
    _git(repo_path, "init")
    _git(repo_path, "config", "user.name", "repo-test")
    _git(repo_path, "config", "user.email", "repo-test@example.com")
    (repo_path / "README.md").write_text("test\n", encoding="utf-8")
    _git(repo_path, "add", "README.md")
    _git(repo_path, "commit", "-m", "init")


def test_build_url_invalid_repo_path_raises() -> None:
    request = URLRequest(path="/path/that/does/not/exist")
    with pytest.raises(URLBuildError, match="Repository path does not exist"):
        build_url(request)


def test_build_url_missing_origin_raises(tmp_path: Path) -> None:
    repo = tmp_path / "repo-no-origin"
    repo.mkdir()
    _init_repo_with_commit(repo)

    request = URLRequest(path=str(repo))
    with pytest.raises(URLBuildError, match="Remote 'origin' was not found"):
        build_url(request)


def test_build_url_from_temp_repo_with_origin(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = tmp_path / "repo-with-origin"
    repo.mkdir()
    _init_repo_with_commit(repo)
    _git(repo, "remote", "add", "origin", "git@github.com:philhanna/repo.git")

    monkeypatch.setattr(
        urlmaker,
        "load_prefix_map",
        lambda: {"git@github.com:": "https://github.com/"},
    )

    request = URLRequest(path=str(repo), issue_flag=True, issue_number=12)
    have = build_url(request)
    assert have == "https://github.com/philhanna/repo/issues/12"


def test_build_url_non_repo_path_raises_actionable_error(tmp_path: Path) -> None:
    not_repo = tmp_path / "plain-dir"
    not_repo.mkdir()

    request = URLRequest(path=str(not_repo))
    with pytest.raises(URLBuildError, match="not a git repository"):
        build_url(request)
