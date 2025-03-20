package main

import (
	"fmt"
	"os"

	"github.com/philhanna/repo"
	"github.com/pkg/browser"
)

// ---------------------------------------------------------------------
// Functions
// ---------------------------------------------------------------------

func main() {

	// Get the url of the repository
	url := repo.GetURL()

	// Ignore bogus warning messages written to stderr
	nullFile, err := os.OpenFile(os.DevNull, os.O_WRONLY, 0644)
	if err != nil {
		fmt.Println("Error opening /dev/null:", err)
		return
	}
	defer nullFile.Close()

	os.Stderr = nullFile

	// Open the browser window
	browser.OpenURL(url)
}
