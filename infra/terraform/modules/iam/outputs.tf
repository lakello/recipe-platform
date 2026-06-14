output "k8s_cluster_sa_id" {
  value = yandex_iam_service_account.k8s_cluster.id
}

output "k8s_node_sa_id" {
  value = yandex_iam_service_account.k8s_node.id
}

output "storage_sa_id" {
  value = yandex_iam_service_account.storage.id
}

output "access_key_id" {
  value       = yandex_iam_service_account_static_access_key.sa_static_storage_access.access_key
  description = "ID статического ключа доступа для Object Storage"
}

output "secret_access_key" {
  value       = yandex_iam_service_account_static_access_key.sa_static_storage_access.secret_key
  description = "Секретный ключ для доступа к Object Storage"
  sensitive   = true
}

output "cicd_sa_id" {
  value = yandex_iam_service_account.cicd.id
}
