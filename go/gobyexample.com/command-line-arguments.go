package main

import "os"
import "fmt"

func main() {
	argsWithProg := os.Args
	argsWithoutProg := os.Args[1:]

	arg := os.Args[3]

	var p = fmt.Println
	p(argsWithProg)
	p(argsWithoutProg)
	p(arg)
}