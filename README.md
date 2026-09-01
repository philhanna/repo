# Repo

[![Go Report Card](https://goreportcard.com/badge/github.com/philhanna/repo)][idGoReportCard]
[![PkgGoDev](https://pkg.go.dev/badge/github.com/philhanna/repo)][idPkgGoDev]

## References

-   [Github repository](https://github.com/philhanna/repo)

## Overview

This program opens a browser window with some page in Github for this
repository. This can be the main repository page, the actions page, the issues
page, or the issue page for a specific issue. The program is designed to be
run from a command line (such as Visual Studio Code's integrated terminal)
**in the repository**.

## Usage

```bash
repo [OPTIONS] [ISSUE]
```

Positional parameter:
- `issue` (optional): issue number source. Accepted examples:
  - `35`
  - `#35`
  - `issue#35`
  - `defect#35-rename`

Options:
- `-h`, `--help`: display help text and exit
- `-a`, `--actions`: route to the repository actions page
- `-i`, `--issue`: route to issues page; if no explicit issue is provided, branch name can supply issue number
- `-p`, `--path`: path to local repository (default `.`)

Examples:
```bash
repo
repo --actions
repo --issue
repo 35
repo --issue defect#35-rename
repo --path ~/src/my-repo --issue
```

## Installation

### Python (current migration target)

From the repository root:

```bash
# pipx (recommended for CLI tools)
pipx install .

# pip
python -m pip install .

# editable development install
python -m pip install -e .

# editable development install with test dependencies
python -m pip install -e .[dev]
```

After installation, run:

```bash
repo --help
```

## Testing

Install development dependencies, then run:

```bash
python -m pip install -e .[dev]
pytest -q
```

### Go (original implementation)

```bash
git clone git@github.com:/philhanna/repo
cd repo
go install .
```
## URL resolution

The program resolves the browser URL from the repository's `origin` remote
automatically, with no configuration file:

- `http://` and `https://` remotes are used as-is.
- SCP-like remotes (`user@host:path`) and `ssh://` remotes
  (`ssh://[user@]host[:port]/path`) are rewritten to `https://host/path`,
  dropping the user, scheme, and port.

This works for any host — GitHub, a self-hosted Gitea/Forgejo instance, etc. —
without per-host configuration.

## Python vs Go — Migration Notes

The Python implementation targets full behavioral parity with the original Go
version. Known differences are listed below:

| Aspect | Go | Python |
|---|---|---|
| Git access | `go-git` library | `git` subprocess (stdlib) |
| Prefix mapping | config file (embedded via `go:embed` + user override) | algorithmic URL rewrite, no config file |
| Browser launch | `github.com/pkg/browser` | stdlib `webbrowser.open` |
| Error output | `log.Fatal` to stderr | concise message to stderr, exit code 1 |
| Entry point | `go install .` then `repo` | `pip install .` then `repo` |

No behavioral differences in issue-number parsing, URL prefix mapping, or
branch-derived issue routing were intentionally introduced.

## Cutover Criteria

The Python implementation is ready to replace the Go version when:

- [x] All 19+ automated tests pass (`pytest -q`).
- [x] Manual smoke test: `repo` opens repository home page from a real git repo.
- [x] Manual smoke test: `repo --issue` opens the issues page.
- [x] Manual smoke test: `repo 35` opens issue #35.
- [x] Manual smoke test: branch-derived issue number is used when `--issue` is
      set and no explicit number is given.
- [x] Verified on Linux.
- [ ] Verified on macOS or Windows.

[idGoReportCard]: https://goreportcard.com/report/github.com/philhanna/repo
[idPkgGoDev]: https://pkg.go.dev/github.com/philhanna/repo
