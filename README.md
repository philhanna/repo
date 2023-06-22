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

## Usage:

```bash
Launches a browser window for a page of the git remote repository.

positional parameters:
  issue          The issue number (optional). This can be:
                 - An integer, e.g., "35"
                 - An integer with a # prefix, e.g., "#35"
                 - A branch name, e.g., "issue#35"
                 - A branch name with a non-numeric suffix, e.g., "defect#35-rename"

options:
  -h, --help     Displays this help text and exits
  -i, --issues   Display the main issues page. If the current branch contains
                 an issue number, use that.
```

## Installation:

cd to a temporary directory and download the repository, then install it:
```bash
git clone git@github.com:/philhanna/repo
cd repo
go install repo/repo.go
```
## Configuration:
The program gets the URL to display by using the repository's main
remote, which is usually `origin`.  It needs to transform the remote name
by modifying its prefix. This is done with a map of remote prefixes
to url prefixes.

This map is stored in a configuration file

Create a subdirectory named `repo` in your user configuration directory, which is:
```
On Linux/Mac: $HOME/.config/repo
On Windows:   %USERPROFILE%\AppData\Roaming\repo
```
Copy `config.yaml` to that directory and add any changes that you encounter
with any of your local repositories. 

[idGoReportCard]: https://goreportcard.com/report/github.com/philhanna/repo
[idPkgGoDev]: https://pkg.go.dev/github.com/philhanna/repo
