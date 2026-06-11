output "cluster_id" {
  description = "ID кластера PostgreSQL"
  value       = yandex_mdb_postgresql_cluster.postgres.id
}

output "fqdn" {
  description = "Полное доменное имя кластера PostgreSQL"
  value       = yandex_mdb_postgresql_cluster.postgres.host[0].fqdn
}

output "db_name" {
  description = "Имя базы данных"
  value       = var.database_name
}

output "db_user" {
  description = "Имя пользователя базы данных"
  value       = var.database_user
}
