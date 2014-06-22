package main

import "fmt"

func main() {
	m := make(map[string]int)

	m["k1"] = 6
	m["k2"] = 13

	fmt.Println(m)
}