package main

import "strings"
import "fmt"

var p = fmt.Println

func main() {
	p("Contains:	", strings.Contains("test", "es"))
	p("Count: 		", strings.Count("test", "t"))
	p("Repeat:		", strings.Repeat("a", 5))
}