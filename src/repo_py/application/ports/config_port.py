"""Outbound port for loading Gitea host/port configuration."""

from __future__ import annotations

from typing import Protocol

from repo_py.domain.models import GiteaConfig


class ConfigPort(Protocol):
    """Abstracts loading of the optional Gitea host/port override.

    Concrete adapters (e.g. one that reads a bundled or user ``.env`` file)
    implement this protocol; the application layer depends only on this
    interface, never on the adapter itself.
    """

    def load_gitea_config(self) -> GiteaConfig | None:
        """Return the configured Gitea host/port override, or ``None``."""
        ...
