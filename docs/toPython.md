# Python Migration Plan

## Goal
- [ ] Rebuild this tool in Python with the same behavior as the Go version: parse CLI args, detect repository/branch/remote, transform remote URL with YAML prefix mapping, optionally route to issues/issue number, and open a browser.

## Phase 1: Baseline and Scope
- [x] Confirm feature parity requirements from current behavior in [README.md](../README.md).
- [x] Capture current behavior and edge cases from [cmdline.go](../cmdline.go), [urlmaker.go](../urlmaker.go), [config.go](../config.go), and [cmd/repo.go](../cmd/repo.go).
- [x] Define non-goals for v1 (for example: no support for remotes beyond `origin` unless explicitly added).

### Phase 1 Decisions (Completed)

#### Parity Requirements (Must Match Go Behavior)
- [x] CLI behavior:
  - [x] Positional `issue` argument is optional.
  - [x] `-i` and `--issue` enable issues routing.
  - [x] `-p` and `--path` accept repository path and default to `.`.
  - [x] Help text stays aligned with current UX and examples.
- [x] Issue parsing behavior:
  - [x] Parse first numeric group from input pattern `#?(\d+)` (case-insensitive input handling).
  - [x] Accept values like `35`, `#35`, `issue#35`, and `defect#35-rename`.
  - [x] Return `0` if no number is present.
- [x] Repository behavior:
  - [x] Open repository at provided path.
  - [x] Read remote named `origin`.
  - [x] Read current branch name from `HEAD`.
- [x] URL construction behavior:
  - [x] Start from first configured `origin` URL.
  - [x] Remove `.git` suffix when present.
  - [x] Convert git-remote prefix to browser URL prefix via YAML `prefixes` map.
  - [x] If `--issue` is set, append `/issues`; append `/<issueNumber>` when resolved.
  - [x] If `--issue` is set and explicit issue argument is missing, derive issue from branch name.
- [x] Config behavior:
  - [x] Load user config from `$XDG_CONFIG_HOME/repo/config.yaml` or equivalent from `os.UserConfigDir()` behavior.
  - [x] Fall back to bundled default config when user config is absent.
- [x] Browser behavior:
  - [x] Open resolved URL in default browser.

#### Captured Edge Cases
- [x] Missing repository path or invalid git repository should fail with clear error.
- [x] Missing `origin` remote should fail with clear error.
- [x] Unsupported remote prefix (not in YAML map) should fail fast.
- [x] Branch-derived issue number is only considered when `--issue` is set.
- [x] Explicit issue argument overrides branch-derived issue when both are available.
- [x] Multiple digit groups in input use the first match.

#### v1 Non-Goals
- [x] No support for selecting remotes other than `origin`.
- [x] No TUI/GUI enhancements beyond opening the browser URL.
- [x] No behavior changes to issue-number parsing semantics.
- [x] No expansion of config schema beyond current `prefixes` mapping.
- [x] No automatic remediation for malformed git remotes; error and exit instead.

## Phase 2: Python Project Skeleton
- [x] Create Python package layout (recommended):
  - [x] `src/repo_py/__init__.py`
  - [x] `src/repo_py/cli.py`
  - [x] `src/repo_py/config.py`
  - [x] `src/repo_py/urlmaker.py`
  - [x] `src/repo_py/main.py`
  - [x] `tests/test_cli.py`
  - [x] `tests/test_urlmaker.py`
- [x] Add packaging metadata with a console entry point (`repo`) via `pyproject.toml`.
- [x] Decide dependency strategy:
  - [x] Use standard library `subprocess` for Git commands.
  - [ ] Use `GitPython` for repo/branch/remote access.
- [x] Add YAML dependency (`PyYAML`).

### Phase 2 Decisions (Completed)
- [x] Chosen Git access approach for v1: use Python standard library (`subprocess`) to avoid adding a second runtime dependency.
- [x] Added Python packaging metadata and script entry point in `pyproject.toml`.
- [x] Added packaged default config file at `src/repo_py/config.yaml` for fallback behavior parity.

## Phase 3: Implement Core Modules
- [x] Implement CLI parsing in `cli.py` using `argparse`:
  - [x] Support positional `issue` input.
  - [x] Support `-i/--issue`.
  - [x] Support `-p/--path` with default `.`.
  - [x] Reproduce help text closely.
- [x] Implement `parse_issue_number()` in `cli.py` with regex behavior matching Go logic.
- [x] Implement config loading in `config.py`:
  - [x] Resolve user config path (`~/.config/repo/config.yaml` on Linux/macOS; platform equivalent on Windows).
  - [x] Fall back to bundled default `config.yaml` when user config is missing.
  - [x] Parse `prefixes` mapping from YAML.
- [x] Implement URL construction in `urlmaker.py`:
  - [x] Open repo at provided path.
  - [x] Read `origin` remote URL.
  - [x] Read current branch name.
  - [x] Trim `.git` suffix if present.
  - [x] Swap remote prefix to web URL prefix based on config mapping.
  - [x] Append `/issues` and optional `/<issue>` according to CLI flags and branch-derived issue.
  - [x] Raise clear errors for missing repo, missing `origin`, or unsupported URL prefixes.
- [x] Implement browser launch in `main.py` using `webbrowser.open`.

## Phase 4: Testing for Parity
- [x] Port existing issue parser tests from [cmdline_test.go](../cmdline_test.go) to pytest parameterized tests.
- [x] Add unit tests for URL prefix swapping and `.git` trimming.
- [x] Add tests for issue-routing behavior:
  - [x] `--issue` only => `/issues`.
  - [x] `--issue` + explicit number => `/issues/<n>`.
  - [x] `--issue` + branch-embedded number => `/issues/<n>` when explicit number is absent.
- [x] Add negative tests:
  - [x] Unsupported remote URL format.
  - [x] Missing `origin` remote.
  - [x] Invalid/non-repo path.
- [x] Add integration tests with temporary git repositories where practical.

## Phase 5: CLI and Packaging UX
- [x] Add executable entry point so users can run `repo` after install.
- [x] Ensure help text and errors are concise and actionable.
- [x] Document install and usage paths (`pipx install .`, `pip install .`, or editable mode).

## Phase 6: Documentation and Rollout
- [x] Update [README.md](../README.md) with Python setup, dependencies, and usage examples.
- [x] Add migration notes describing differences from Go implementation (if any).
- [x] Keep Go implementation during transition and run side-by-side validation on real repositories.
- [x] Define cutover criteria (all tests passing + manual smoke tests on Linux and Windows/macOS).

## Phase 7: Validation Checklist (Pre-Cutover)
- [ ] Running `repo` from a git repository opens the repository home page.
- [ ] Running `repo --issue` opens issues page (or issue page when number available).
- [ ] Branch-derived issue number parsing matches existing behavior.
- [ ] User config overrides default prefix mappings.
- [ ] Behavior is verified in at least one Linux and one non-Linux environment.

## Suggested Implementation Order
- [x] 1) Build `parse_issue_number()` + tests.
- [x] 2) Build config loader + tests.
- [x] 3) Build URL generation + tests.
- [x] 4) Wire CLI to URL generation + browser opener.
- [x] 5) Finish docs and release packaging.
