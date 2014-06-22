package main

import "fmt"

func vals() (int, int) {
	return 3, 6
}

func main() {
	a, b := vals()
	fmt.Println(a)
	fmt.Println(b)

	_, c := vals()
	fmt.Println(c)
}