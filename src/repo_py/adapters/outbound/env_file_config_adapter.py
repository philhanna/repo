"""Outbound adapter that loads Gitea config from an ``.env``-style file."""

from __future__ import annotations

from pathlib import Path
import os
import re

from repo_py.domain.models import GiteaConfig

PACKAGE_NAME = "repo"

_ASSIGNMENT_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)$")


class EnvFileConfigAdapter:
    """:class:`~repo_py.application.ports.config_port.ConfigPort` backed by a ``.env`` file.

    Looks for a user config file at the path returned by
    :meth:`_get_user_config_path`. If that file does not exist, the bundled
    ``config.env`` shipped alongside this adapter is used instead.
    """

    def load_gitea_config(self) -> GiteaConfig | None:
        """Load the Gitea host/port override.

        The ``.env`` file may define ``GITEA_HOST`` and ``GITEA_PORT``, e.g.::

            GITEA_HOST="localhost"
            GITEA_PORT="3000"

        Returns:
            The parsed :class:`GiteaConfig`, or ``None`` if either variable
            is missing from the config file.
        """
        user_config = self._get_user_config_path()
        if user_config.exists():
            data = user_config.read_text(encoding="utf-8")
        else:
            bundled = Path(__file__).with_name("config.env")
            data = bundled.read_text(encoding="utf-8")

        env = self._parse_env(data)
        host = env.get("GITEA_HOST")
        port = env.get("GITEA_PORT")
        if not host or not port:
            return None
        return GiteaConfig(host=host, port=int(port))

    def _get_user_config_path(self) -> Path:
        """Return the expected user config file path.

        Respects the ``XDG_CONFIG_HOME`` environment variable when set;
        otherwise falls back to ``~/.config/repo/config.env``.

        Returns:
            Absolute :class:`~pathlib.Path` to the user-level config file.
            The file is not guaranteed to exist.
        """
        config_home = os.environ.get("XDG_CONFIG_HOME")
        if config_home:
            return Path(config_home) / PACKAGE_NAME / "config.env"
        return Path.home() / ".config" / PACKAGE_NAME / "config.env"

    def _parse_env(self, data: str) -> dict[str, str]:
        """Parse ``KEY=VALUE`` lines from ``.env``-formatted text.

        Blank lines and lines starting with ``#`` are ignored. Values may
        optionally be wrapped in matching single or double quotes, which
        are stripped.

        Args:
            data: Raw contents of a ``.env`` file.

        Returns:
            Dictionary of parsed key/value pairs, in file order.
        """
        result: dict[str, str] = {}
        for line in data.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            match = _ASSIGNMENT_RE.match(line)
            if not match:
                continue
            key, value = match.group(1), match.group(2).strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            result[key] = value
        return result
