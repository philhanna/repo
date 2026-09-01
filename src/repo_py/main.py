"""Application entry point and composition root for the repo Python port."""

from __future__ import annotations

import sys

from repo_py.adapters.inbound.cli import parse_command_line
from repo_py.adapters.outbound.env_file_config_adapter import EnvFileConfigAdapter
from repo_py.adapters.outbound.git_cli_adapter import GitCLIAdapter
from repo_py.adapters.outbound.webbrowser_adapter import WebBrowserAdapter
from repo_py.application.open_repository_url import OpenRepositoryURL
from repo_py.domain.errors import URLBuildError
from repo_py.domain.models import URLRequest


def main() -> int:
    """CLI entrypoint for resolving and opening repository URLs.

    Parses command-line arguments, constructs a
    :class:`~repo_py.domain.models.URLRequest`, resolves it to a URL via
    :func:`build_url`, and opens it in the default web browser.

    Returns:
        ``0`` on success, ``1`` if URL construction fails (error written to
        ``stderr``).
    """
    cmd = parse_command_line()
    request = URLRequest(
        actions_flag=cmd.actions_flag,
        issue_flag=cmd.issue_flag,
        issue_number=cmd.issue_number,
        path=cmd.path,
    )

    try:
        url = build_url(request)
    except URLBuildError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    WebBrowserAdapter().open(url)
    return 0


def build_url(request: URLRequest) -> str:
    """Resolve *request* into a URL, wiring up the default outbound adapters.

    Args:
        request: Parsed CLI intent describing what page to open.

    Returns:
        Fully formed URL ready to open in a browser.

    Raises:
        URLBuildError: If the repository path does not exist or is not a
            directory, or if any git query or URL construction step fails.
    """
    use_case = OpenRepositoryURL(GitCLIAdapter(), EnvFileConfigAdapter())
    return use_case.execute(request)


if __name__ == "__main__":
    raise SystemExit(main())
