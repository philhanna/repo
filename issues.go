package main

import (
	"flag"
	"fmt"
	"log"
	"os"
	"regexp"
	"strconv"
	"strings"

	"github.com/pkg/browser"

	git "github.com/go-git/go-git/v5"
)

const (
	GIT_SUFFIX    = ".git"
	GITHUB_PREFIX = "git@github.com:"
	HTTP_PREFIX   = "http:"
	HTTPS_PREFIX  = "https:"
	MY_PREFIX     = "https://github.com"
	NO_ISSUE      = -1
)

// ---------------------------------------------------------------------
// Functions
// ---------------------------------------------------------------------

// init sets up the usage text
func init() {
	flag.Usage = func() {
		fmt.Fprintf(os.Stderr, `usage: issues [OPTIONS] [ISSUE]
Launches a browser window with the "issues" page of the specified repository.

positional arguments:
  issue          The issue number (optional). This can be`+
			`
		- An integer, e.g., "35"
		- An integer with a # prefix, e.g., "#35"
		- A branch name, e.g., "issue#35"
		- A branch name with a non-numeric suffix, e.g., "defect#35-rename"

options:
  -h             Displays this help text and exits
`)
	}
}

// parseIssueNumber extracts a number from a string parameter, if there
// is one.  Returns NO_ISSUE, if not.
func parseIssueNumber(s string) int {
	re := regexp.MustCompile(`#?(\d+)`)
	m := re.FindSubmatch([]byte(s))
	if m == nil || len(m) < 2 {
		return NO_ISSUE
	}
	mString := string(m[1])
	issue, _ := strconv.Atoi(mString)
	return issue
}

func main() {

	var (
		err   error = nil
		issue int   = NO_ISSUE
	)

	// Get command line arguments
	flag.Parse()
	if flag.NArg() > 0 {
		issue = parseIssueNumber(flag.Arg(0))
	}

	path := "."

	// Get the repository at that path
	repo, err := git.PlainOpen(path)
	if err != nil {
		log.Fatal(err)
	}

	// From the repository, get the "origin" remote
	remote, err := repo.Remote("origin")
	if err != nil {
		log.Fatal(err)
	}

	// From the remote, get the first configured URL
	url := remote.Config().URLs[0]

	// Trim any ".git" suffix
	if strings.HasSuffix(url, GIT_SUFFIX) {
		url = strings.TrimSuffix(url, ".git")
	}

	// Handle this URL according to its type:
	switch {
	case strings.HasPrefix(url, GITHUB_PREFIX):
		url = GetURLFromGitURL(url)
	case strings.HasPrefix(url, HTTP_PREFIX):
		// OK
	case strings.HasPrefix(url, HTTPS_PREFIX):
		// OK
	default:
		log.Fatalf("Unsupported url type: %s\n", url)
	}

	// Append the issue number, if one was specified
	issuesURL := url + "/issues"
	if issue != NO_ISSUE {
		issuesURL = fmt.Sprintf("%s/%d", issuesURL, issue)
	}

	// Display the issue page in the browser
	browser.OpenURL(issuesURL)
}

// GetURLFromGitURL changes a git@github.com: prefix to https://github.com
func GetURLFromGitURL(url string) string {
	url = strings.TrimPrefix(url, GITHUB_PREFIX)
	url = strings.Join([]string{MY_PREFIX, url}, "/")
	return url
}
