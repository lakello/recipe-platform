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

output "kubernetes_sg_id" {
  value       = module.network.kubernetes_sg_id
  description = "Идентификатор созданной группы безопасности для Kubernetes узлов"
}

#kubernetes module

output "cluster_id" {
  value       = module.kubernetes.cluster_id
  description = "Идентификатор созданного кластера Kubernetes"
}

output "cluster_name" {
  value       = module.kubernetes.cluster_name
  description = "Имя созданного кластера Kubernetes"
}

output "system_node_group_id" {
  value       = module.kubernetes.system_node_group_id
  description = "Идентификатор созданной системной группы узлов Kubernetes"
}

output "app_node_group_id" {
  value       = module.kubernetes.app_node_group_id
  description = "Идентификатор созданной группы узлов для приложений Kubernetes"
}
