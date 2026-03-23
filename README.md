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
```

After installation, run:

```bash
repo --help
```

### Go (original implementation)

```bash
git clone git@github.com:/philhanna/repo
cd repo
go install .
```
## Configuration:
The program gets the URL to display by using the repository's main
remote, which is usually `origin`.  It needs to transform the remote name
by modifying its prefix. This is done with a map of remote prefixes
to url prefixes.

This map is stored in a configuration file.

Create a subdirectory named `repo` in your user configuration directory, which is:
```
On Linux/Mac: $HOME/.config/repo
On Windows:   %USERPROFILE%\AppData\Roaming\repo
```
Copy `config.yaml` to that directory and make any changes needed to recognize
anything different in the remotes of your local repositories. 

[idGoReportCard]: https://goreportcard.com/report/github.com/philhanna/repo
[idPkgGoDev]: https://pkg.go.dev/github.com/philhanna/repo
