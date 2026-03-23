"""Configuration loading for prefix mapping."""

from __future__ import annotations

from pathlib import Path
from typing import Any
import os

import yaml


PACKAGE_NAME = "repo"


def get_user_config_path() -> Path:
    """Return the expected user config file path."""
    config_home = os.environ.get("XDG_CONFIG_HOME")
    if config_home:
        return Path(config_home) / PACKAGE_NAME / "config.yaml"
    return Path.home() / ".config" / PACKAGE_NAME / "config.yaml"


def load_prefix_map() -> dict[str, str]:
    """Load git-prefix to web-prefix mapping from user or bundled config."""
    user_config = get_user_config_path()
    if user_config.exists():
        data = user_config.read_text(encoding="utf-8")
    else:
        bundled = Path(__file__).with_name("config.yaml")
        data = bundled.read_text(encoding="utf-8")

    parsed: dict[str, Any] = yaml.safe_load(data) or {}
    prefixes = parsed.get("prefixes")
    if not isinstance(prefixes, dict):
        raise ValueError("Invalid config: expected 'prefixes' mapping")

    result: dict[str, str] = {}
    for key, value in prefixes.items():
        if isinstance(key, str) and isinstance(value, str):
            result[key] = value
    return result
