"""URL construction helpers for the repo Python port."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class URLRequest:
    issue_flag: bool = False
    issue_number: int = 0
    path: str = "."


def build_url(_request: URLRequest) -> str:
    """Build a browser URL from repository state and CLI intent."""
    raise NotImplementedError("Phase 3 will implement URL generation.")
