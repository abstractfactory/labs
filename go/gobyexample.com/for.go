package main

import "fmt"
import "io/ioutil"


func main() {
	i := 1
	for i <= 3 {
		fmt.Println(i)
		i++
	}

	for j := 7; j <= 9; j++ {
		fmt.Println(j)
	}

	for {
		fmt.Println("loop")
		break
	}

	files, _ := ioutil.ReadDir("/home/marcus")
	for i, f := range files {
		fmt.Println(f.Name())
		fmt.Println(i)
	} 
}