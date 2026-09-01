"""Use case: resolve a repository page request into a browser-ready URL."""

from __future__ import annotations

from pathlib import Path

from repo_py.application.ports.config_port import ConfigPort
from repo_py.application.ports.git_port import GitPort
from repo_py.domain.errors import URLBuildError
from repo_py.domain.models import URLRequest
from repo_py.domain.services import build_url_from_parts


class OpenRepositoryURL:
    """Builds the destination URL for a requested repository page.

    Depends only on the :class:`~repo_py.application.ports.git_port.GitPort`
    and :class:`~repo_py.application.ports.config_port.ConfigPort`
    interfaces, never on their concrete adapters.
    """

    def __init__(self, git_port: GitPort, config_port: ConfigPort) -> None:
        self._git = git_port
        self._config = config_port

    def execute(self, request: URLRequest) -> str:
        """Resolve *request* against the local repository into a URL.

        Args:
            request: Parsed CLI intent describing what page to open.

        Returns:
            Fully formed URL ready to open in a browser.

        Raises:
            URLBuildError: If the repository path does not exist or is not
                a directory, or if any git query or URL construction step
                fails.
        """
        repo_path_obj = Path(request.path).expanduser()
        if not repo_path_obj.exists():
            raise URLBuildError(f"Repository path does not exist: {repo_path_obj}")
        if not repo_path_obj.is_dir():
            raise URLBuildError(f"Repository path is not a directory: {repo_path_obj}")

        repo_path = str(repo_path_obj)
        branch_name = self._git.get_current_branch(repo_path)
        remote_url = self._git.get_remote_url(repo_path, "origin")
        gitea_config = self._config.load_gitea_config()
        return build_url_from_parts(request, remote_url, branch_name, gitea_config)
