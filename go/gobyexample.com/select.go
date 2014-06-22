package main

import "time"
import "fmt"

func test(message string) string {
	time.Sleep(time.Second)
	return message
}

func main() {
	channel1 := make(chan string)
	channel2 := make(chan string)

	// go func() {
	// 	time.Sleep(time.Second * 1)
	// 	channel1 <- "one"
	// }()

	// go func() {
	// 	time.Sleep(time.Second * 2)
	// 	channel2 <- "two"
	// }()

	for i := 0; i < 2; i++ {
		select {
		case message := test("My Message"):
			fmt.Println("received", message)
		// case message1 := <- channel1:
		// 	fmt.Println("received", message1)
		// case message2 := <- channel2:
		// 	fmt.Println("received", message2)
		}
	}
}