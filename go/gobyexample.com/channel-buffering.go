package main

import "fmt"

func main() {
	messages := make(chan string, 2)

	messages <- "buffered"
	messages <- "channel"
	messages <- "channel2"

	fmt.Println(<-messages)
	fmt.Println(<-messages)
}