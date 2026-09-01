"""URL construction helpers for the repo Python port."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import subprocess

from repo_py.cli import parse_issue_number
from repo_py.config import GiteaConfig, load_gitea_config

_SCP_LIKE_RE = re.compile(r"^(?:[\w.-]+@)?([^/:]+):/?(.+)$")


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


class URLBuildError(RuntimeError):
    """Raised when URL construction cannot be completed.

    Wraps lower-level errors (missing git binary, path not a repository,
    unknown remote URL scheme, etc.) with a human-readable message suitable
    for display on ``stderr``.
    """


def _run_git(path: str, args: list[str]) -> str:
    """Run a git command in the target repository and return stripped stdout.

    Args:
        path: Working directory in which to execute git (the repository root).
        args: Git sub-command and arguments, e.g.
            ``["remote", "get-url", "origin"]``.

    Returns:
        Stripped standard output produced by the git command.

    Raises:
        URLBuildError: If git is not installed, the path is not a git
            repository, the requested remote does not exist, HEAD is
            ambiguous, or the command fails for any other reason.
    """
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=path,
            check=True,
            capture_output=True,
            text=True,
        )
        return completed.stdout.strip()
    except FileNotFoundError as exc:
        raise URLBuildError(
            "Could not run git. Ensure git is installed and the repository path exists."
        ) from exc
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip()
        command = " ".join(args)

        if "not a git repository" in stderr.lower():
            raise URLBuildError(f"Path is not a git repository: {path}") from exc

        if args[:3] == ["remote", "get-url", "origin"] and "No such remote" in stderr:
            raise URLBuildError(
                f"Remote 'origin' was not found in repository: {path}"
            ) from exc

        if args[:3] == ["rev-parse", "--abbrev-ref", "HEAD"] and "ambiguous argument 'HEAD'" in stderr:
            raise URLBuildError(
                "Could not determine current branch. Create an initial commit first."
            ) from exc

        raise URLBuildError(stderr or f"git {command} failed") from exc


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
        gitea_config: Host/port override for a self-hosted Gitea instance,
            as loaded by :func:`~repo_py.config.load_gitea_config`. When
            *remote_url*'s host matches, the URL is built as
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


def build_url(request: URLRequest) -> str:
    """Build a browser URL from repository state and CLI intent.

    Validates the repository path, queries git for the current branch and
    origin remote URL, loads the Gitea host/port override from config, then
    delegates to :func:`build_url_from_parts`.

    Args:
        request: Parsed CLI intent describing what page to open.

    Returns:
        Fully formed URL ready to open in a browser.

    Raises:
        URLBuildError: If the repository path does not exist or is not a
            directory, or if any git command or URL construction step fails.
    """
    repo_path_obj = Path(request.path).expanduser()
    if not repo_path_obj.exists():
        raise URLBuildError(f"Repository path does not exist: {repo_path_obj}")
    if not repo_path_obj.is_dir():
        raise URLBuildError(f"Repository path is not a directory: {repo_path_obj}")

    repo_path = str(repo_path_obj)
    branch_name = _run_git(repo_path, ["rev-parse", "--abbrev-ref", "HEAD"])
    remote_url = _run_git(repo_path, ["remote", "get-url", "origin"])
    return build_url_from_parts(request, remote_url, branch_name, load_gitea_config())
