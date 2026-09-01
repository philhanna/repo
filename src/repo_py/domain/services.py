"""Pure domain logic for repository URL construction.

Every function here operates only on values already in hand (strings,
:class:`~repo_py.domain.models.URLRequest`,
:class:`~repo_py.domain.models.GiteaConfig`) and performs no I/O, so it can
be tested and reused without a git checkout, network access, or a config
file on disk.
"""

from __future__ import annotations

import re

from repo_py.domain.errors import URLBuildError
from repo_py.domain.models import GiteaConfig, URLRequest

_SCP_LIKE_RE = re.compile(r"^(?:[\w.-]+@)?([^/:]+):/?(.+)$")


def build_url_from_parts(
    request: URLRequest,
    remote_url: str,
    branch_name: str,
    gitea_config: GiteaConfig | None = None,
) -> str:
    """Build the destination URL from known git values.

    Normalises the remote URL to its web equivalent (see
    :func:`normalize_remote_url`) and appends either ``/actions`` when
    :attr:`URLRequest.actions_flag` is set or ``/issues[/<number>]`` when
    :attr:`URLRequest.issue_flag` is set.

    If :attr:`URLRequest.issue_flag` is ``True`` and
    :attr:`URLRequest.issue_number` is ``0``, an issue number is extracted
    from the current branch name as a convenience.

    Args:
        request: Parsed CLI intent describing what page to open.
        remote_url: Raw remote URL returned by ``git remote get-url origin``.
        branch_name: Current branch returned by
            ``git rev-parse --abbrev-ref HEAD``.
        gitea_config: Host/port override for a self-hosted Gitea instance.
            When *remote_url*'s host matches, the URL is built as
            ``http://<host>:<port>/...`` instead of the generic
            ``https://<host>/...`` form.

    Returns:
        Fully formed URL ready to open in a browser.

    Raises:
        URLBuildError: If *remote_url* does not match a recognized git
            remote form.
    """
    issue_number = request.issue_number
    if request.issue_flag and issue_number == 0:
        branch_issue_number = parse_issue_number(branch_name)
        if branch_issue_number != 0:
            issue_number = branch_issue_number

    url = normalize_remote_url(remote_url, gitea_config)

    if request.actions_flag:
        url += "/actions"
    elif request.issue_flag:
        url += "/issues"
        if issue_number != 0:
            url += f"/{issue_number}"

    return url


def parse_issue_number(value: str) -> int:
    """Extract the first issue number from a string; return 0 if not found.

    Accepts a variety of formats such as ``"35"``, ``"#35"``, ``"issue#35"``,
    or ``"defect#35-rename"``.  The search is case-insensitive.

    Args:
        value: Raw string that may contain an issue number.

    Returns:
        The first integer found in *value*, or ``0`` when no digits are
        present or *value* is empty.
    """
    if not value:
        return 0
    match = re.search(r"#?(\d+)", value.upper())
    if not match:
        return 0
    return int(match.group(1))


def normalize_remote_url(url: str, gitea_config: GiteaConfig | None = None) -> str:
    """Convert a git remote URL into its web equivalent.

    Already-``http(s)://`` URLs are returned unchanged. SCP-like remotes
    (``user@host:path``, including the ``user@host:/path`` form ``git``
    itself normalises ``ssh://`` GitHub remotes to) and ``ssh://`` remotes
    (``ssh://[user@]host[:port]/path``) have their user and scheme dropped.
    The result is ``https://host/path``, unless *gitea_config* is given and
    its host matches, in which case it is ``http://host:port/path``.

    Args:
        url: Raw remote URL, as returned by ``git remote get-url origin``.
        gitea_config: Host/port override for a self-hosted Gitea instance.

    Returns:
        The corresponding web URL.

    Raises:
        URLBuildError: If *url* does not match a recognized git remote form.
    """
    if url.endswith(".git"):
        url = url[: -len(".git")]

    if url.startswith("http://") or url.startswith("https://"):
        return url

    host, path = _extract_host_and_path(url)

    if gitea_config is not None and host == gitea_config.host:
        return f"http://{host}:{gitea_config.port}/{path}"

    return f"https://{host}/{path}"


def _extract_host_and_path(url: str) -> tuple[str, str]:
    """Extract the host and path from an ``ssh://`` or SCP-like git remote.

    Args:
        url: Remote URL, with any ``.git`` suffix and ``http(s)://`` scheme
            already ruled out by the caller.

    Returns:
        A ``(host, path)`` tuple.

    Raises:
        URLBuildError: If *url* does not match a recognized git remote form.
    """
    if url.startswith("ssh://"):
        rest = url[len("ssh://") :]
        host_and_maybe_user, _, path = rest.partition("/")
        host = host_and_maybe_user.rpartition("@")[2]
        host = host.partition(":")[0]
        if host and path:
            return host, path
        raise URLBuildError(f"Unsupported url type: {url}")

    match = _SCP_LIKE_RE.match(url)
    if match:
        return match.groups()

    raise URLBuildError(f"Unsupported url type: {url}")
