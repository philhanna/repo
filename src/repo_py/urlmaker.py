"""URL construction helpers for the repo Python port."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess

from repo_py.cli import parse_issue_number
from repo_py.config import load_prefix_map


@dataclass(slots=True)
class URLRequest:
    """Encapsulates the intent and context needed to build a repository URL.

    Attributes:
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


class URLBuildError(RuntimeError):
    """Raised when URL construction cannot be completed.

    Wraps lower-level errors (missing git binary, path not a repository,
    unknown remote URL scheme, etc.) with a human-readable message suitable
    for display on ``stderr``.
    """


def swap_prefix(url: str, from_prefix: str, to_prefix: str) -> str:
    """Replace the leading URL prefix with a target prefix.

    Args:
        url: Original URL whose prefix should be replaced.
        from_prefix: The prefix to remove from the start of *url*.
        to_prefix: The replacement prefix to prepend.

    Returns:
        New URL string with *from_prefix* replaced by *to_prefix*.  If
        *url* does not start with *from_prefix*, the original string is
        returned unchanged.
    """
    return to_prefix + url.removeprefix(from_prefix)


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
    prefix_map: dict[str, str],
) -> str:
    """Build the destination URL from known git and config values.

    Normalises the remote URL (stripping ``.git`` suffix and converting
    ``ssh://`` variants to SCP-style ``git@`` form), applies the first
    matching prefix substitution from *prefix_map*, and appends an
    ``/issues[/<number>]`` path when :attr:`URLRequest.issue_flag` is set.

    If :attr:`URLRequest.issue_flag` is ``True`` and
    :attr:`URLRequest.issue_number` is ``0``, an issue number is extracted
    from the current branch name as a convenience.

    Args:
        request: Parsed CLI intent describing what page to open.
        remote_url: Raw remote URL returned by ``git remote get-url origin``.
        branch_name: Current branch returned by
            ``git rev-parse --abbrev-ref HEAD``.
        prefix_map: Mapping of git URL prefixes to web URL prefixes, as
            loaded by :func:`~repo_py.config.load_prefix_map`.

    Returns:
        Fully formed HTTPS URL ready to open in a browser.

    Raises:
        URLBuildError: If no entry in *prefix_map* matches *remote_url*.
    """
    issue_number = request.issue_number
    if request.issue_flag and issue_number == 0:
        branch_issue_number = parse_issue_number(branch_name)
        if branch_issue_number != 0:
            issue_number = branch_issue_number

    url = remote_url
    if url.startswith("ssh://git@github.com/"):
        url = "git@github.com:/" + url.removeprefix("ssh://git@github.com/")
    if url.endswith(".git"):
        url = url[: -len(".git")]

    for prefix, new_prefix in prefix_map.items():
        if url.startswith(prefix):
            url = swap_prefix(url, prefix, new_prefix)
            break
    else:
        raise URLBuildError(f"Unsupported url type: {url}")

    if request.issue_flag:
        url += "/issues"
        if issue_number != 0:
            url += f"/{issue_number}"

    return url


def build_url(request: URLRequest) -> str:
    """Build a browser URL from repository state and CLI intent.

    Validates the repository path, queries git for the current branch and
    origin remote URL, loads the prefix map from config, then delegates to
    :func:`build_url_from_parts`.

    Args:
        request: Parsed CLI intent describing what page to open.

    Returns:
        Fully formed HTTPS URL ready to open in a browser.

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
    return build_url_from_parts(request, remote_url, branch_name, load_prefix_map())
