"""Configuration loading for prefix mapping."""

from __future__ import annotations

from pathlib import Path
from typing import Any
import os

import yaml


PACKAGE_NAME = "repo"


def get_user_config_path() -> Path:
    """Return the expected user config file path.

    Respects the ``XDG_CONFIG_HOME`` environment variable when set; otherwise
    falls back to ``~/.config/repo/config.yaml``.

    Returns:
        Absolute :class:`~pathlib.Path` to the user-level config file.  The
        file is not guaranteed to exist.
    """
    config_home = os.environ.get("XDG_CONFIG_HOME")
    if config_home:
        return Path(config_home) / PACKAGE_NAME / "config.yaml"
    return Path.home() / ".config" / PACKAGE_NAME / "config.yaml"


def load_prefix_map() -> dict[str, str]:
    """Load git-prefix to web-prefix mapping from user or bundled config.

    Looks for a user config file at the path returned by
    :func:`get_user_config_path`.  If that file does not exist, the bundled
    ``config.yaml`` shipped with the package is used instead.

    The YAML file must contain a top-level ``prefixes`` mapping where each
    key is a git remote URL prefix and the corresponding value is the
    replacement web URL prefix.

    Returns:
        Dictionary mapping git URL prefixes to their web equivalents.

    Raises:
        ValueError: If the loaded config does not contain a valid
            ``prefixes`` mapping.
    """
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
