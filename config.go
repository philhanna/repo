package repo

import (
	_ "embed"
	yaml "gopkg.in/yaml.v2"
	"log"
	"os"
	"path/filepath"
)

// ---------------------------------------------------------------------
// Type definitions
// ---------------------------------------------------------------------

type Config struct {
	PREFIXES map[string]string `yaml:"prefixes"`
}

// ---------------------------------------------------------------------
// Constants and variables
// ---------------------------------------------------------------------

const PACKAGE_NAME = "repo"

// go:embed config.yaml
var DEFAULT_CONFIG_DATA []byte

// ---------------------------------------------------------------------
// Functions
// ---------------------------------------------------------------------

// GetPrefixMap returns a map of git remote prefixes to URL prefixes
// that are needed to find the actual repository on the web.  It will
// look for the config.yaml configuration file in the $HOME/.config/repo
// directory.  If it is not there, it will use the default one in
// the current directory
func GetPrefixMap() map[string]string {

	var err error
	var configData []byte

	// Look for a local YAML file with the configuration
	configDir, _ := os.UserConfigDir()
	filename := filepath.Join(configDir, PACKAGE_NAME, "config.yaml")
	configData, err = os.ReadFile(filename)

	// If there is no local file, use the default values
	if err != nil {
		configData = DEFAULT_CONFIG_DATA
	}

	// Now create a map of prefixes to substitution values
	config := new(Config)
	err = yaml.Unmarshal(configData, config)
	if err != nil {
		log.Fatal(err)
	}

	return config.PREFIXES
}
