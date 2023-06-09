package repo

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func Test_parseIssueNumber(t *testing.T) {
	tests := []struct {
		name string
		s    string
		want int
	}{
		{"Empty string", "", 0},
		{"No digits string", "bogus", 0},
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
