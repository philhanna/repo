package main

import (
	"fmt"
	"log"
	"testing"

	"github.com/stretchr/testify/assert"
	git "gopkg.in/src-d/go-git.v4"
)

func Test_parseIssueNumber(t *testing.T) {
	tests := []struct {
		name string
		s    string
		want int
	}{
		{"Empty string", "", ALL_ISSUES_PAGE},
		{"No digits string", "bogus", BAD_ISSUE},
		{"Simple integer", "3", 3},
		{"Multidigit integer", "35", 35},
		{"With octothorpe", "#35", 35},
		{"With prefix", "issue#17", 17},
		{"In branch name", "defect#35-rename", 35},
		{"With multiple groups of numbers", "1 2 3", 1},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			want := tt.want
			have := ParseIssueNumber(tt.s)
			assert.Equal(t, want, have)
		})
	}
}

func TestRepo_GetBranchName(t *testing.T) {
	branchName := GetBranchName()
	fmt.Printf("DEBUG: branch name is %q\n", branchName)
}

func GetBranchName() string {

	// Open the git repository
	repo, err := git.PlainOpen(".")
	if err != nil {
		log.Println("Could not open repository")
		log.Fatal(err)
	}
	
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
