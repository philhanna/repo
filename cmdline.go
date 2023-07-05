package repo

import (
	"flag"
	"fmt"
	"log"
	"os"
	"regexp"
	"strconv"
	"strings"
)

// ---------------------------------------------------------------------
// Type Definitions
// ---------------------------------------------------------------------

type CommandLine struct {
	issueFlag   bool
	IssueNumber int
	Path        string
}

func (cmd CommandLine) String() string {
	parts := []string{
		fmt.Sprintf("issueFlag=%t", cmd.issueFlag),
		fmt.Sprintf("IssueNumber=%d", cmd.IssueNumber),
		fmt.Sprintf("Path=%v", cmd.Path),
	}
	return strings.Join(parts, ",")
}

// ---------------------------------------------------------------------
// Functions
// ---------------------------------------------------------------------

// init sets up the usage text and logging defaults
func init() {
	log.SetFlags(log.LstdFlags | log.Lshortfile)
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
  -h, --help     Displays this help text and exits
  -i, --issue    Display the main issues page. If the current branch contains
                 an issue number, use that.
  -p, --path     Path to local repository (Default is ".")
`)
	}
}

// ParseCommandLine extracts the options on the command line
func ParseCommandLine() *CommandLine {

	cmd := new(CommandLine)

	// Get command line arguments
	flag.BoolVar(&cmd.issueFlag, "i", false, "Display the main issues page")
	flag.BoolVar(&cmd.issueFlag, "issue", false, "Display the main issues page")
	flag.StringVar(&cmd.Path, "p", "", `Path to local repository (Default=".")`)
	flag.StringVar(&cmd.Path, "path", "", `Path to local repository (Default=".")`)

	flag.Parse()

	// Get the issue number, if specified
	if flag.NArg() > 0 {
		cmd.IssueNumber = ParseIssueNumber(flag.Arg(0))
	}

	// Get path or use default path
	if cmd.Path == "" {
		cmd.Path = "."
	}

	return cmd
}

// ParseIssueNumber extracts a number from a string parameter, if there
// is one.  Returns 0, if not.
func ParseIssueNumber(s string) int {
	if s == "" {
		return 0
	}
	s = strings.ToUpper(s)
	re := regexp.MustCompile(`#?(\d+)`)
	m := re.FindSubmatch([]byte(s))
	if m == nil || len(m) < 2 {
		return 0
	}
	mString := string(m[1])
	issue, _ := strconv.Atoi(mString)
	return issue
}
