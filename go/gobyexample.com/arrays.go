package main

import "fmt"

func main() {
	var a [5]int
	fmt.Println("emp:", a)

	a[4] = 100
	fmt.Println("set:", a)
	fmt.Println("get:", a[4])

	b := [5]int{1, 2, 10, 20, 100}
	fmt.Println("dcl:", b)

	var twoD [2][3]int
	for i := 0; i < 2; i++ {
		for j := 0; j < 3; j++ {
			twoD[i][j] = i + j
		}
	}

	fmt.Println("2d:", twoD)

	var matrix [3][3][3]int
	for i := 0; i < 3; i++ {
		for j := 0; j < 3; j++ {
			for g := 0; g < 3; g++ {
				matrix[i][j][g] = i + j + g
			}
		}
	}

	fmt.Println("matrix:", matrix)

}