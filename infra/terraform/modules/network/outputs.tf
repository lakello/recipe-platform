output "vpc_id" {
  value       = yandex_vpc_network.this.id
  description = "Идентификатор созданной VPC сети"
}

output "public_subnet_id" {
  value       = yandex_vpc_subnet.public_subnet.id
  description = "Идентификатор созданной публичной подсети"
}

output "private_subnet_id" {
  value       = yandex_vpc_subnet.private_subnet.id
  description = "Идентификатор созданной приватной подсети"
}

output "public_sg_id" {
  value       = yandex_vpc_security_group.public_sg.id
  description = "Идентификатор созданной публичной группы безопасности"
}

output "private_sg_id" {
  value       = yandex_vpc_security_group.private_sg.id
  description = "Идентификатор созданной приватной группы безопасности"
}

output "database_sg_id" {
  value       = yandex_vpc_security_group.database_sg.id
  description = "Идентификатор созданной группы безопасности базы данных"
}
