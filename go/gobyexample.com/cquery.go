// cQuery - Content Object Model traversal with Open Metadata
//
// Usage:
//  To return all matches of class "Asset":
// 		$ cquery ".Asset"
//
//  To return all matches of ID "MyFolder":
// 		$ cquery "#MyFolder"
//
//  To return all matches of name "SomeFolder":
// 		$ cquery "MyFolder"
//

package main

import "os"
import "fmt"
import "strings"
import "flag"
import "path/filepath"

func walk(path string, query string) []string {
	// Recursively walk through `path` in search for `query`
	results := make([]string, 0)

	var scan = func(path string, info os.FileInfo, _ error) error {

		// Skip hidden folders
		if strings.HasPrefix(info.Name(), ".") {
			return filepath.SkipDir
		}

		// Look for `query` within `path`
		if info.IsDir() {
			var filename string = filepath.Join(path, query)
			if _, err := os.Stat(filename); err == nil {
				fmt.Println("  ", path)
				results = append(results, path)
			}
		}
		return nil
	}

	filepath.Walk(path, scan)
	return results
}

func main() {
	CONTAINER := ".meta"
	workingdir, _ := os.Getwd()

	// Parse arguments
	queryPtr := flag.String("query", "", "Query")
	flag.Parse()

	query := flag.Arg(0)
	if *queryPtr != "" {
		query = *queryPtr
	}

	// fmt.Println("Seaching", workingdir, "for:", query)

	// Append Open Metadata container to query.
	// This is where metadata of this sort is stored.
	if strings.HasPrefix(query, ".") {
		query = filepath.Join(CONTAINER, query[1:]+".class")
	} else if strings.HasPrefix(query, "#") {
		query = filepath.Join(CONTAINER, query[1:]+".id")
	} else {
		query = filepath.Join(CONTAINER, query)
	}

	// Commence query
	results := walk(workingdir, query)
	if len(results) == 0 {
		fmt.Println("   No results")
	}
}
