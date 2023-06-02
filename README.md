# Repo
[![Go Report Card](https://goreportcard.com/badge/github.com/philhanna/repo)][idGoReportCard]
[![PkgGoDev](https://pkg.go.dev/badge/github.com/philhanna/repo)][idPkgGoDev]


## References
- [Github repository](https://github.com/philhanna/repo)
  
## Overview

This program opens a browser window with some page in Github for this
repository. This can be either the main repository page, the issues page, or
the issue page for a specific issue. The program is designed to be run from a
command line (such as Visual Studio Code's integrated terminal) in the
repository.

## Usage:
```bash
usage: repo [OPTIONS] [ISSUE]
Launches a browser window for a page of the git remote repository.

positional parameters:
  issue          The issue number (optional). This can be:
                 - An integer, e.g., "35"
                 - An integer with a # prefix, e.g., "#35"
                 - A branch name, e.g., "issue#35"
                 - A branch name with a non-numeric suffix, e.g., "defect#35-rename"

options:
  -h             Displays this help text and exits
  -i             Display the main issues page```
```


[idGoReportCard]: https://goreportcard.com/report/github.com/philhanna/repo
[idPkgGoDev]: https://pkg.go.dev/github.com/philhanna/repo
