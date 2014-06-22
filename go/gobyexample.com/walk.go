package main

import "os"
import "fmt"
import "io/ioutil"
import "path/filepath"


func visit(path string, info os.FileInfo, err error) error {
	// Search each folder's contained .meta directory for
	// the class "Asset".

	if filepath.Base(path) == ".meta" { return nil }
	
	var metapath string = filepath.Join(path, ".meta")
	files, _ := ioutil.ReadDir(metapath)

	for _, file := range files {
		if file.Name() == "Asset.class" {
			fmt.Println(path)
		}
	}

	return nil
}

func main() {
	filepath.Walk("/home/marcus/studio", visit)
}