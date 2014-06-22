package main

import "fmt"
import "time"

func main() {
	messages := make(chan string)

	go func() { 
		time.Sleep(1000 * time.Millisecond)
		messages <- "ping"

	}()

	msg := <-messages
	fmt.Println(msg)
}