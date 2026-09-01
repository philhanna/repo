"""Tests for the env-file-backed ConfigPort adapter."""

from __future__ import annotations

from pathlib import Path

import pytest

from repo_py.adapters.outbound.env_file_config_adapter import EnvFileConfigAdapter
from repo_py.domain.models import GiteaConfig


def test_load_gitea_config_bundled_default() -> None:
    have = EnvFileConfigAdapter().load_gitea_config()
    assert have == GiteaConfig(host="localhost", port=3000)


def test_load_gitea_config_reads_user_override(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    user_config_dir = tmp_path / "repo"
    user_config_dir.mkdir()
    (user_config_dir / "config.env").write_text(
        'GITEA_HOST="git.example.com"\nGITEA_PORT="8080"\n',
        encoding="utf-8",
    )
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    have = EnvFileConfigAdapter().load_gitea_config()
    assert have == GiteaConfig(host="git.example.com", port=8080)


def test_load_gitea_config_returns_none_when_incomplete(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    user_config_dir = tmp_path / "repo"
    user_config_dir.mkdir()
    (user_config_dir / "config.env").write_text('GITEA_HOST="git.example.com"\n', encoding="utf-8")
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    assert EnvFileConfigAdapter().load_gitea_config() is None
