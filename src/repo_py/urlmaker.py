"""URL construction helpers for the repo Python port."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess

from repo_py.cli import parse_issue_number
from repo_py.config import load_prefix_map


@dataclass(slots=True)
class URLRequest:
    issue_flag: bool = False
    issue_number: int = 0
    path: str = "."


class URLBuildError(RuntimeError):
    """Raised when URL construction cannot be completed."""


def swap_prefix(url: str, from_prefix: str, to_prefix: str) -> str:
    """Replace the leading URL prefix with a target prefix."""
    return to_prefix + url.removeprefix(from_prefix)


def _run_git(path: str, args: list[str]) -> str:
    """Run a git command in the target repository and return stripped stdout."""
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
    """Build the destination URL from known git and config values."""
    issue_number = request.issue_number
    if request.issue_flag and issue_number == 0:
        branch_issue_number = parse_issue_number(branch_name)
        if branch_issue_number != 0:
            issue_number = branch_issue_number

    url = remote_url
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
    """Build a browser URL from repository state and CLI intent."""
    repo_path_obj = Path(request.path).expanduser()
    if not repo_path_obj.exists():
        raise URLBuildError(f"Repository path does not exist: {repo_path_obj}")
    if not repo_path_obj.is_dir():
        raise URLBuildError(f"Repository path is not a directory: {repo_path_obj}")

    repo_path = str(repo_path_obj)
    branch_name = _run_git(repo_path, ["rev-parse", "--abbrev-ref", "HEAD"])
    remote_url = _run_git(repo_path, ["remote", "get-url", "origin"])
    return build_url_from_parts(request, remote_url, branch_name, load_prefix_map())
