"""Outbound adapter that queries git via the ``git`` command-line tool."""

from __future__ import annotations

import subprocess

from repo_py.domain.errors import URLBuildError


class GitCLIAdapter:
    """:class:`~repo_py.application.ports.git_port.GitPort` backed by ``git``."""

    def get_current_branch(self, repo_path: str) -> str:
        """Return the current branch name for the repository at *repo_path*."""
        return self._run_git(repo_path, ["rev-parse", "--abbrev-ref", "HEAD"])

    def get_remote_url(self, repo_path: str, remote_name: str) -> str:
        """Return the raw remote URL for *remote_name* in the repository at *repo_path*."""
        return self._run_git(repo_path, ["remote", "get-url", remote_name])

    def _run_git(self, path: str, args: list[str]) -> str:
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

            if args[:2] == ["remote", "get-url"] and "No such remote" in stderr:
                raise URLBuildError(
                    f"Remote '{args[2]}' was not found in repository: {path}"
                ) from exc

            if args[:3] == ["rev-parse", "--abbrev-ref", "HEAD"] and "ambiguous argument 'HEAD'" in stderr:
                raise URLBuildError(
                    "Could not determine current branch. Create an initial commit first."
                ) from exc

            raise URLBuildError(stderr or f"git {command} failed") from exc
