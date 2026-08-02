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

output "ingress_sg_id" {
  value = module.network.ingress_sg_id
}

output "postgresql_sg_id" {
  value = module.network.postgresql_sg_id
}

output "redis_sg_id" {
  value = module.network.redis_sg_id
}

output "control_plane_sg_id" {
  value = module.network.control_plane_sg_id
}

output "nodes_sg_id" {
  value = module.network.nodes_sg_id
}

#kubernetes module

output "kubernetes_cluster_id" {
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

#postgres module

output "postgres_cluster_id" {
  description = "ID кластера PostgreSQL"
  value       = module.postgres.cluster_id
}

output "fqdn" {
  description = "Полное доменное имя кластера PostgreSQL"
  value       = module.postgres.fqdn
}

output "db_name" {
  description = "Имя базы данных"
  value       = module.postgres.db_name
}

output "db_user" {
  description = "Имя пользователя базы данных"
  value       = module.postgres.db_user
}

#redis module

output "redis_cluster_id" {
  description = "ID кластера Redis"
  value       = module.redis.cluster_id
}

output "redis_fqdn" {
  description = "Полное доменное имя кластера Redis"
  value       = module.redis.fqdn
}

#compute module

output "bastion_instance_id" {
  description = "ID созданного инстанса"
  value       = module.compute.instance_id
}

output "bastion_public_ip" {
  description = "Статический публичный IP-адрес (для Ansible-инвентаря)"
  value       = module.compute.public_ip
}

output "bastion_internal_ip" {
  description = "Внутренний IP-адрес инстанса"
  value       = module.compute.internal_ip
}

#dns module

output "dns_zone_id" {
  description = "ID созданной DNS-зоны"
  value       = module.dns.zone_id
}

output "dns_name_servers" {
  description = "Список авторитетных DNS-серверов Yandex Cloud"
  value       = module.dns.name_servers
}

#iam module

output "object_storage_access_key_id" {
  value       = module.iam.access_key_id
  description = "ID статического ключа доступа для Object Storage"
}

output "object_storage_secret_access_key" {
  value       = module.iam.secret_access_key
  description = "Секретный ключ для доступа к Object Storage"
  sensitive   = true
}

output "image_pusher_sa_id" {
  value = module.iam.image_pusher_sa_id
}

output "deployer_sa_id" {
  value = module.iam.deployer_sa_id
}
