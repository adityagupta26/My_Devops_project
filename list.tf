variable users {
	type = list
	default = ["a", "k", "a"]
}

output printfirst {
	value = " first value of user is ${var.users[0]}"
}
