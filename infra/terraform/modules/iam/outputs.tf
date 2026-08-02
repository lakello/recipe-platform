output "k8s_cluster_sa_id" {
  value = yandex_iam_service_account.k8s_cluster.id

  depends_on = [
    yandex_resourcemanager_folder_iam_member.k8s_cluster_roles,
  ]
}

output "k8s_node_sa_id" {
  value = yandex_iam_service_account.k8s_node.id

  depends_on = [
    yandex_resourcemanager_folder_iam_member.k8s_node_roles,
  ]
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

output "image_pusher_sa_id" {
  value = yandex_iam_service_account.image_pusher.id
}

output "deployer_sa_id" {
  value = yandex_iam_service_account.deployer.id
}
