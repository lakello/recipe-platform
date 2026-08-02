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

output "ingress_sg_id" {
  value = yandex_vpc_security_group.ingress_sg.id
}

output "postgresql_sg_id" {
  value = yandex_vpc_security_group.postgresql_sg.id
}

output "redis_sg_id" {
  value = yandex_vpc_security_group.redis_sg.id
}

output "control_plane_sg_id" {
  value = yandex_vpc_security_group.control_plane_sg.id
}

output "nodes_sg_id" {
  value = yandex_vpc_security_group.nodes_sg.id
}
