variable "userage" {
	type = map
	default = {
		a = 25
		k = 24
	}
}

variable "username" {
	type = string
}

output "userage" {
	value = "my name is ${var.username} and my age is ${lookup(var.userage, "a")}"
}
