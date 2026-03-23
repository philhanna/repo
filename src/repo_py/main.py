"""Application entry point for the repo Python port."""

from __future__ import annotations

from repo_py.cli import parse_command_line


def main() -> int:
    """CLI entrypoint placeholder until URL logic is implemented."""
    _ = parse_command_line()
    raise SystemExit("Not implemented yet. Complete Phase 3 to enable execution.")


if __name__ == "__main__":
    raise SystemExit(main())
