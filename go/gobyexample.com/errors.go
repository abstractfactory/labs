package main

import "errors"
import "fmt"


func f1(arg int) (int, error) {
	if arg == 42 {
		return -1, errors.New("Can't work with this number")
	}

	return arg + 3, nil
}

type argError struct {
	arg int
	prob string
}

func (err *argError) Error() string {
	return fmt.Sprintf("%d - %s", err.arg, err.prob)
}

func f2(arg int) (int, error) {
	if arg == 42 {
		return -1, &argError{arg, "can't work with it"}
	}
	return arg + 3, nil
}

func main() {
	for _, i := range []int{7, 42, 12, 31, 110} {

		if result, err := f1(i); err != nil {
			fmt.Println("f1 failed:", err)
		} else {
			fmt.Println("f1 worked", result)
		}
	}

	for _, i := range []int{7, 42, 11, 42, 501} {
		if result, err := f2(i); err != nil {
			fmt.Println("f2 failed:", err)
		} else {
			fmt.Println("f2 worked:", result)
		}
	}
}