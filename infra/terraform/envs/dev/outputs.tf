#network module

output "vpc_id" {
  value       = module.network.vpc_id
  description = "Идентификатор созданной VPC сети"
}

output "public_subnet_id" {
  value       = module.network.public_subnet_id
  description = "Идентификатор созданной публичной подсети"
}

output "private_subnet_id" {
  value       = module.network.private_subnet_id
  description = "Идентификатор созданной приватной подсети"
}

output "public_sg_id" {
  value       = module.network.public_sg_id
  description = "Идентификатор созданной публичной группы безопасности"
}

output "private_sg_id" {
  value       = module.network.private_sg_id
  description = "Идентификатор созданной приватной группы безопасности"
}

output "database_sg_id" {
  value       = module.network.database_sg_id
  description = "Идентификатор созданной группы безопасности базы данных"
}
