package main

import (
	"log"
	"os"
	"path/filepath"
	_ "embed"
	yaml "gopkg.in/yaml.v2"
)

const PACKAGE_NAME = "repo"

// go:embed config.yaml
var DEFAULT_MAP_DATA []byte

// GetPrefixMap returns a map of git remote prefixes to URL prefixes
// that are needed to find the actual repository on the web.  It will
// look for the config.yaml configuration file in the $HOME/.config/repo
// directory.  If it is not there, it will use the default one in
// the current directory
func GetPrefixMap() map[string]string {

	// Create an empty map
	prefixMap := new(map[string]string)

	// Look for a local YAML file with the configuration
	configDir, _ := os.UserConfigDir()
	filename := filepath.Join(configDir, PACKAGE_NAME, "config.yaml")
	prefixMapData, err := os.ReadFile(filename)

	// If there is no local file, use the default values
	if err != nil {
		prefixMapData = DEFAULT_MAP_DATA
	}

	// Now create a map of prefixes to substitution values
	err = yaml.Unmarshal(prefixMapData, prefixMap)
	if err != nil {
		log.Fatal(err)
	}

	return *prefixMap
}
