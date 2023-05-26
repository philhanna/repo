package main

import (
	"flag"
	"fmt"
	"log"
	"os"
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
)

// ---------------------------------------------------------------------
// Functions
// ---------------------------------------------------------------------

func init() {
	flag.Usage = func() {
		fmt.Fprintf(os.Stderr, `usage: issues [OPTIONS] [PATH]
Launches a browser window with the "issues" page of the specified repository.

positional arguments:
  path           local path to repository (default: ".")
  issue          the integer issue number (optional)

options:
  -h             displays this help text and exits
`)
	}
}
func IsInteger(s string) bool {
	_, err := strconv.Atoi(s)
	return err == nil
}

func main() {

	var path string
	var issue string

	// Get command line arguments
	flag.Parse()
	args := flag.Args()
	switch len(args) {
	case 1:
		switch IsInteger(args[0]) {
		case true:
			issue = args[0]
		case false:
			path = args[0]
		}
	case 2:
		path = args[0]
		issue = args[1]
	}

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
	case strings.HasPrefix(url, HTTPS_PREFIX):
	default:
		log.Fatalf("Unsupported url type: %s\n", url)
	}

	parts := []string{
		url,
		"issues",
	}
	if issue != "" {
		parts = append(parts, issue)
	}
	issuesURL := strings.Join(parts, "/")

	browser.OpenURL(issuesURL)
}

// GetURLFromGitURL changes a git@github.com: prefix to https://github.com
func GetURLFromGitURL(url string) string {
	url = strings.TrimPrefix(url, GITHUB_PREFIX)
	url = strings.Join([]string{MY_PREFIX, url}, "/")
	return url
}
