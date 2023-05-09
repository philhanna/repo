package main

import (
	"flag"
	"fmt"
	"log"
	"os"
	"strings"

	git "github.com/go-git/go-git/v5"
)

// ---------------------------------------------------------------------
// Functions
// ---------------------------------------------------------------------

func init() {
	flag.Usage = func() {
		fmt.Fprintf(os.Stderr, `usage: issues [-h] <path>

issues: Launches a browser window with the "issues" page of the specified repository.

positional arguments:
  path           local path to repository (default: ".")

options:
  -h             displays this help text and exits
`)
	}
}

func main() {
	const (
		GIT_SUFFIX    = ".git"
		GITHUB_PREFIX = "git@github.com:"
		MY_PREFIX     = "https://github.com"
	)

	flag.Parse()

	url, err := GetRemoteURL(".")
	if err != nil {
		log.Fatalf("Could not get remote URL: %v", err)
	}

	if strings.HasSuffix(url, GIT_SUFFIX) {
		url = strings.TrimSuffix(url, ".git")
	}
	if strings.HasPrefix(url, GITHUB_PREFIX) {
		url = strings.TrimPrefix(url, GITHUB_PREFIX)
		url = strings.Join([]string{MY_PREFIX, url}, "/")
	}
	fmt.Printf("%v\n", url)

	// browser.OpenURL(issuesURL)
}

func GetRemoteURL(path string) (string, error) {

	repo, err := GetRepository(path)
	if err != nil {
		return "", err
	}

	// From the repository, get the origin remote
	remote, err := repo.Remote("origin")
	if err != nil {
		return "", err
	}

	// Return the first URL
	url := remote.Config().URLs[0]

	return url, nil
}

// GetRepository returns a pointer to the specified repository
func GetRepository(path string) (*git.Repository, error) {
	repo, err := git.PlainOpen(path)
	if err != nil {
		return nil, err
	}
	return repo, nil
}


func GetRemote(repo *git.Repository) (*git.Remote, error) {
	remote, err := repo.Remote("origin")
	return remote, err
}
