package main

import (
	"fmt"
	"log"

	git "github.com/go-git/go-git/v5"
)

// ---------------------------------------------------------------------
// Functions
// ---------------------------------------------------------------------

func main() {
	issuesURL, err := GetIssuesURL()
	if err != nil {
		log.Fatalf("Could not get issues URL: %v", err)
	}
	_ = issuesURL
	// browser.OpenURL(issuesURL)
}

func GetIssuesURL() (any, error) {
	
	// Get a pointer to the repository

	repo, err := git.PlainOpen(".")
	if err != nil {
		return nil, err
	}
	
	remote, err := repo.Remote("origin")
	if err != nil {
		return nil, err
	}

	fmt.Printf("DEBUG: remote=%v\n", remote)
	return nil, nil
}
