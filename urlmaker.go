package repo

import (
	"fmt"
	"log"
	"strings"

	git "github.com/go-git/go-git/v5"
)

// ---------------------------------------------------------------------
// Functions
// ---------------------------------------------------------------------

// GetBranchName returns a string representing the current branch in the
// specified repository.
func GetBranchName(repository git.Repository) string {

	// Retrieve the current branch reference:

	ref, err := repository.Head()
	if err != nil {
		log.Println("Could not get the HEAD reference")
		log.Fatal(err)
	}

	// Extract the branch name from the reference

	branchName := ref.Name().Short()

	return branchName
}

// GetURL creates the URL that will display the repository, either the
// main page or the issues page or the desired issue number.
func GetURL() string {

	cmd := ParseCommandLine()
	fmt.Printf("cmd=%s\n", cmd)

	// Get the repository at that path

	repository, err := git.PlainOpen(cmd.Path)
	if err != nil {
		log.Fatal(err)
	}

	// From the repository, get the "origin" remote

	remote, err := repository.Remote("origin")
	if err != nil {
		log.Fatal(err)
	}

	// From the repository, get the branch name.  If it contains an
	// integer, use that as the issue number.

	branchName := GetBranchName(*repository)
	if cmd.issueFlag {
		branchIssueNumber := ParseIssueNumber(branchName)
		if branchIssueNumber != 0 {
			if cmd.IssueNumber == 0 {
				cmd.IssueNumber = branchIssueNumber
			}
		}
	}

	// From the remote, get the first configured URL. We need to convert
	// this from a remote name to the actual URL that can access what
	// the user wants.

	url := remote.Config().URLs[0]

	// Trim any ".git" suffix

	if strings.HasSuffix(url, ".git") {
		url = strings.TrimSuffix(url, ".git")
	}

	// Mutate the URL according to its type according to the
	// configuration YAML.

	prefixes := GetPrefixMap()
	found := false
	for prefix, newPrefix := range prefixes {
		if strings.HasPrefix(url, prefix) {
			url = SwapPrefix(url, prefix, newPrefix)
			found = true
			break
		}
	}
	if !found {
		log.Fatalf("Unsupported url type: %s\n", url)
	}

	// Append the issue number, if one was specified

	if cmd.issueFlag {
		url += "/issues"
		if cmd.IssueNumber != 0 {
			url += fmt.Sprintf("/%d", cmd.IssueNumber)
		}
	}

	return url
}

// SwapPrefix substitutes the usable URL prefix for the one used in the
// git remote value
func SwapPrefix(url, fromPrefix, toPrefix string) string {
	url = strings.TrimPrefix(url, fromPrefix)
	url = toPrefix + url
	return url
}
