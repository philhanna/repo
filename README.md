# Repo

[![Go Report Card](https://goreportcard.com/badge/github.com/philhanna/repo)][idGoReportCard]
[![PkgGoDev](https://pkg.go.dev/badge/github.com/philhanna/repo)][idPkgGoDev]

## References

-   [Github repository](https://github.com/philhanna/repo)

## Overview

This program opens a browser window with some page in Github for this
repository. This can be either the main repository page, the issues page, or
the issue page for a specific issue. The program is designed to be run from a
command line (such as Visual Studio Code's integrated terminal) **in the
repository**.

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
- `-i`, `--issue`: route to issues page; if no explicit issue is provided, branch name can supply issue number
- `-p`, `--path`: path to local repository (default `.`)

Examples:
```bash
repo
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
## Configuration

The program resolves the browser URL from the repository's `origin` remote by
swapping its prefix with the corresponding web URL prefix. This mapping lives in
a YAML config file.

Create a subdirectory named `repo` in your user config directory and place a
`config.yaml` file there:

```
Linux / macOS:  $HOME/.config/repo/config.yaml
Windows:        %USERPROFILE%\AppData\Roaming\repo\config.yaml
```

If no user config is found the bundled default (`src/repo_py/config.yaml`) is
used as a fallback. Default prefix mappings:

```yaml
prefixes:
  "http:": "http:"
  "https:": "https:"
  "git@github.com:/": "https://github.com/"
  "git@github.com:": "https://github.com/"
  "ssh://git@localhost": "http://localhost:3000"
  "git@localhost:": "http://localhost:3000/"
```

## Python vs Go — Migration Notes

The Python implementation targets full behavioral parity with the original Go
version. Known differences are listed below:

| Aspect | Go | Python |
|---|---|---|
| Git access | `go-git` library | `git` subprocess (stdlib) |
| Config fallback | embedded via `go:embed` | bundled `config.yaml` next to package |
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
