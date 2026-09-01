"""Outbound port for opening a URL in the user's browser."""

from __future__ import annotations

from typing import Protocol


class BrowserPort(Protocol):
    """Abstracts opening a URL in a browser.

    Concrete adapters (e.g. one backed by the standard library
    :mod:`webbrowser` module) implement this protocol; the application
    layer depends only on this interface, never on the adapter itself.
    """

    def open(self, url: str) -> None:
        """Open *url* in the user's default browser."""
        ...
