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
	GIT_SUFFIX       = ".git"
	GITHUB_PREFIX    = "git@github.com:"
	GITEA_PREFIX     = "ssh://git@localhost"
	HTTP_PREFIX      = "http:"
	HTTPS_PREFIX     = "https:"
	MY_GITHUB_PREFIX = "https://github.com"
	MY_GITEA_PREFIX  = "http://localhost:3000"
	ALL_ISSUES_PAGE  = 0
	NO_ISSUE         = -1
)

// ---------------------------------------------------------------------
// Functions
// ---------------------------------------------------------------------

// init sets up the usage text
func init() {
	flag.Usage = func() {
		fmt.Fprintf(os.Stderr, `usage: repo [OPTIONS] [ISSUE]
Launches a browser window for a page of the git remote repository.

positional parameters:
  issue          The issue number (optional). This can be:
                 - An integer, e.g., "35"
                 - An integer with a # prefix, e.g., "#35"
                 - A branch name, e.g., "issue#35"
                 - A branch name with a non-numeric suffix, e.g., "defect#35-rename"

options:
  -h             Displays this help text and exits
  -i             Display the main issues page. If the current branch contains
                 an issue number, use that.
`)
	}
}

func main() {

	issue := NO_ISSUE
	issueFlag := false

	// Get command line arguments
	flag.BoolVar(&issueFlag, "i", false, "Display the main issues page")
	flag.Parse()

	type Option byte
	const (
		REPO_ONLY Option = iota
		ALL_ISSUES
		SPECIFIC_ISSUE
	)
	var option Option

	switch {
	case flag.NArg() > 0:
		// If a valid issue was specified
		option = SPECIFIC_ISSUE
		issueString := flag.Arg(0)
		issue = ParseIssueNumber(issueString)
		if issue == NO_ISSUE || issue == ALL_ISSUES_PAGE {
			option = REPO_ONLY
		}
	case issueFlag:
		// Will display the main issues page
		option = ALL_ISSUES
	default:
		// Display the main repo page
		option = REPO_ONLY
	}

	// This directory
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

	// From the repository, get the branch name
	branchName := GetBranchName(*repo)

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
	case strings.HasPrefix(url, GITEA_PREFIX):
		url = GetURLFromGiteaURL(url)
	case strings.HasPrefix(url, HTTP_PREFIX):
		// OK
	case strings.HasPrefix(url, HTTPS_PREFIX):
		// OK
	default:
		log.Fatalf("Unsupported url type: %s\n", url)
	}

	// Append the issue number, if one was specified, or display the repo only
	switch option {
	case REPO_ONLY:
		// URL is already OK
	case ALL_ISSUES:
		url += "/issues"
		branchIssue := ParseIssueNumber(branchName)
		if branchIssue != NO_ISSUE {
			url += fmt.Sprintf("/%d", branchIssue)
		}
	case SPECIFIC_ISSUE:
		url += "/issues"
		url += fmt.Sprintf("/%d", issue)
	default:
		// Just the main repo page
	}

	// Display the page in the browser
	browser.OpenURL(url)
}

// GetBranchName returns a string representing the current branch in the
// specified repository.
func GetBranchName(repo git.Repository) string {

	// Retrieve the current branch reference:
	ref, err := repo.Head()
	if err != nil {
		log.Println("Could not get the HEAD reference")
		log.Fatal(err)
	}

	// Extract the branch name from the reference
	branchName := ref.Name().Short()

	return branchName
}

// GetURLFromGitURL changes a git@github.com: prefix to https://github.com
func GetURLFromGitURL(url string) string {
	url = strings.TrimPrefix(url, GITHUB_PREFIX)
	url = strings.Join([]string{MY_GITHUB_PREFIX, url}, "/")
	return url
}

// GetURLFromGiteaURL changes a ssh://git@localhost prefix to http://localhost:3000
func GetURLFromGiteaURL(url string) string {
	url = strings.TrimPrefix(url, GITEA_PREFIX)
	url = strings.Join([]string{MY_GITEA_PREFIX, url}, "/")
	return url
}

// ParseIssueNumber extracts a number from a string parameter, if there
// is one.  Returns NO_ISSUE, if not.
func ParseIssueNumber(s string) int {
	if s == "" {
		return ALL_ISSUES_PAGE
	}
	s = strings.ToUpper(s)
	re := regexp.MustCompile(`#?(\d+)`)
	m := re.FindSubmatch([]byte(s))
	if m == nil || len(m) < 2 {
		return NO_ISSUE
	}
	mString := string(m[1])
	issue, _ := strconv.Atoi(mString)
	return issue
}
