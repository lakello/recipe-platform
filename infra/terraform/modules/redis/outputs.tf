output "cluster_id" {
  description = "ID кластера Redis"
  value       = yandex_mdb_redis_cluster.redis.id
}

output "fqdn" {
  description = "Полное доменное имя кластера Redis"
  value       = yandex_mdb_redis_cluster.redis.host[0].fqdn
}
