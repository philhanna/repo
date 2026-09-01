"""Outbound port for querying git repository state."""

from __future__ import annotations

from typing import Protocol


class GitPort(Protocol):
    """Abstracts the git operations needed to resolve a repository's URL.

    Concrete adapters (e.g. one that shells out to the ``git`` binary)
    implement this protocol; the application layer depends only on this
    interface, never on the adapter itself.
    """

    def get_current_branch(self, repo_path: str) -> str:
        """Return the current branch name for the repository at *repo_path*."""
        ...

    def get_remote_url(self, repo_path: str, remote_name: str) -> str:
        """Return the raw remote URL for *remote_name* in the repository at *repo_path*."""
        ...
