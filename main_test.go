package main

import (
	"reflect"
	"testing"
)

func TestGetIssuesURL(t *testing.T) {
	tests := []struct {
		name    string
		want    any
		wantErr bool
	}{
		{"foo", "x", false},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := GetIssuesURL()
			if (err != nil) != tt.wantErr {
				t.Errorf("GetIssuesURL() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !reflect.DeepEqual(got, tt.want) {
				t.Errorf("GetIssuesURL() = %v, want %v", got, tt.want)
			}
		})
	}
}
