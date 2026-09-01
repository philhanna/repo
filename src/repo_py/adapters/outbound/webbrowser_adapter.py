"""Outbound adapter that opens URLs using the standard library ``webbrowser`` module."""

from __future__ import annotations

import webbrowser


class WebBrowserAdapter:
    """:class:`~repo_py.application.ports.browser_port.BrowserPort` backed by :mod:`webbrowser`."""

    def open(self, url: str) -> None:
        """Open *url* in the user's default browser."""
        webbrowser.open(url)
