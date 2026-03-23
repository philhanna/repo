# Python Migration Plan

## Goal
- [ ] Rebuild this tool in Python with the same behavior as the Go version: parse CLI args, detect repository/branch/remote, transform remote URL with YAML prefix mapping, optionally route to issues/issue number, and open a browser.

## Phase 1: Baseline and Scope
- [ ] Confirm feature parity requirements from current behavior in [README.md](../README.md).
- [ ] Capture current behavior and edge cases from [cmdline.go](../cmdline.go), [urlmaker.go](../urlmaker.go), [config.go](../config.go), and [cmd/repo.go](../cmd/repo.go).
- [ ] Define non-goals for v1 (for example: no support for remotes beyond `origin` unless explicitly added).

## Phase 2: Python Project Skeleton
- [ ] Create Python package layout (recommended):
  - [ ] `src/repo_py/__init__.py`
  - [ ] `src/repo_py/cli.py`
  - [ ] `src/repo_py/config.py`
  - [ ] `src/repo_py/urlmaker.py`
  - [ ] `src/repo_py/main.py`
  - [ ] `tests/test_cli.py`
  - [ ] `tests/test_urlmaker.py`
- [ ] Add packaging metadata with a console entry point (`repo`) via `pyproject.toml`.
- [ ] Decide dependency strategy:
  - [ ] Use standard library `subprocess` for Git commands, or
  - [ ] Use `GitPython` for repo/branch/remote access.
- [ ] Add YAML dependency (`PyYAML`).

## Phase 3: Implement Core Modules
- [ ] Implement CLI parsing in `cli.py` using `argparse`:
  - [ ] Support positional `issue` input.
  - [ ] Support `-i/--issue`.
  - [ ] Support `-p/--path` with default `.`.
  - [ ] Reproduce help text closely.
- [ ] Implement `parse_issue_number()` in `cli.py` with regex behavior matching Go logic.
- [ ] Implement config loading in `config.py`:
  - [ ] Resolve user config path (`~/.config/repo/config.yaml` on Linux/macOS; platform equivalent on Windows).
  - [ ] Fall back to bundled default `config.yaml` when user config is missing.
  - [ ] Parse `prefixes` mapping from YAML.
- [ ] Implement URL construction in `urlmaker.py`:
  - [ ] Open repo at provided path.
  - [ ] Read `origin` remote URL.
  - [ ] Read current branch name.
  - [ ] Trim `.git` suffix if present.
  - [ ] Swap remote prefix to web URL prefix based on config mapping.
  - [ ] Append `/issues` and optional `/<issue>` according to CLI flags and branch-derived issue.
  - [ ] Raise clear errors for missing repo, missing `origin`, or unsupported URL prefixes.
- [ ] Implement browser launch in `main.py` using `webbrowser.open`.

## Phase 4: Testing for Parity
- [ ] Port existing issue parser tests from [cmdline_test.go](../cmdline_test.go) to pytest parameterized tests.
- [ ] Add unit tests for URL prefix swapping and `.git` trimming.
- [ ] Add tests for issue-routing behavior:
  - [ ] `--issue` only => `/issues`.
  - [ ] `--issue` + explicit number => `/issues/<n>`.
  - [ ] `--issue` + branch-embedded number => `/issues/<n>` when explicit number is absent.
- [ ] Add negative tests:
  - [ ] Unsupported remote URL format.
  - [ ] Missing `origin` remote.
  - [ ] Invalid/non-repo path.
- [ ] Add integration tests with temporary git repositories where practical.

## Phase 5: CLI and Packaging UX
- [ ] Add executable entry point so users can run `repo` after install.
- [ ] Ensure help text and errors are concise and actionable.
- [ ] Document install and usage paths (`pipx install .`, `pip install .`, or editable mode).

## Phase 6: Documentation and Rollout
- [ ] Update [README.md](../README.md) with Python setup, dependencies, and usage examples.
- [ ] Add migration notes describing differences from Go implementation (if any).
- [ ] Keep Go implementation during transition and run side-by-side validation on real repositories.
- [ ] Define cutover criteria (all tests passing + manual smoke tests on Linux and Windows/macOS).

## Phase 7: Validation Checklist (Pre-Cutover)
- [ ] Running `repo` from a git repository opens the repository home page.
- [ ] Running `repo --issue` opens issues page (or issue page when number available).
- [ ] Branch-derived issue number parsing matches existing behavior.
- [ ] User config overrides default prefix mappings.
- [ ] Behavior is verified in at least one Linux and one non-Linux environment.

## Suggested Implementation Order
- [ ] 1) Build `parse_issue_number()` + tests.
- [ ] 2) Build config loader + tests.
- [ ] 3) Build URL generation + tests.
- [ ] 4) Wire CLI to URL generation + browser opener.
- [ ] 5) Finish docs and release packaging.
