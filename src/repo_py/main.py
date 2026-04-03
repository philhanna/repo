"""Application entry point for the repo Python port."""

from __future__ import annotations

import sys
import webbrowser

from repo_py.cli import parse_command_line
from repo_py.urlmaker import URLBuildError, URLRequest, build_url


def main() -> int:
    """CLI entrypoint for resolving and opening repository URLs.

    Parses command-line arguments, constructs a :class:`~repo_py.urlmaker.URLRequest`,
    builds the target URL via :func:`~repo_py.urlmaker.build_url`, and opens it
    in the default web browser.

    Returns:
        ``0`` on success, ``1`` if URL construction fails (error written to
        ``stderr``).
    """
    cmd = parse_command_line()
    request = URLRequest(
        issue_flag=cmd.issue_flag,
        issue_number=cmd.issue_number,
        path=cmd.path,
    )

    try:
        url = build_url(request)
    except URLBuildError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    webbrowser.open(url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
