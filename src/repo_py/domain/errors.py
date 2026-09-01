"""Domain-level errors for repository URL construction."""

from __future__ import annotations


class URLBuildError(RuntimeError):
    """Raised when URL construction cannot be completed.

    Wraps lower-level errors (missing git binary, path not a repository,
    unknown remote URL scheme, etc.) with a human-readable message suitable
    for display on ``stderr``.
    """
