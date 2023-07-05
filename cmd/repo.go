package main

import (
	"github.com/philhanna/repo"
	"github.com/pkg/browser"
)

// ---------------------------------------------------------------------
// Functions
// ---------------------------------------------------------------------

func main() {
	url := repo.GetURL()
	browser.OpenURL(url)
}