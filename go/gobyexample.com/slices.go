package main

import "fmt"

func main() {
	s := make([]string, 3)
	fmt.Println("emp:", s)

	s[0] = "Abra"
	s[1] = "Kadabra"
	s[2] = "Magic!"
	fmt.Println("set:", s)
	fmt.Println("get:", s[2])

	fmt.Println("len:", len(s))
}