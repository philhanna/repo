"""Domain models for the repo Python port."""

from __future__ import annotations

from dataclasses import dataclass
from typing import NamedTuple


@dataclass(slots=True)
class URLRequest:
    """Encapsulates the intent and context needed to build a repository URL.

    Attributes:
        actions_flag: When ``True``, the resulting URL should point to the
            repository actions page.
        issue_flag: When ``True``, the resulting URL should point to the
            issues page rather than the repository root or a specific branch.
        issue_number: Explicit issue number to append to the issues URL, or
            ``0`` to navigate to the issues index.  Ignored when
            *issue_flag* is ``False``.
        path: Filesystem path to the local git repository used to resolve
            the remote URL and current branch (defaults to the current
            working directory).
    """

    issue_flag: bool = False
    issue_number: int = 0
    path: str = "."
    actions_flag: bool = False


class GiteaConfig(NamedTuple):
    """Host and port of a self-hosted Gitea instance.

    Attributes:
        host: Gitea server hostname, e.g. ``"localhost"``.
        port: Gitea web UI port, e.g. ``3000``.
    """

    host: str
    port: int
