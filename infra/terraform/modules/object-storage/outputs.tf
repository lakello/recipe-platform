output "access_key_id" {
  value       = yandex_iam_service_account_static_access_key.access_key.access_key
  description = "ID статического ключа доступа для Object Storage"
}

output "secret_access_key" {
  value       = yandex_iam_service_account_static_access_key.access_key.secret_key
  description = "Секретный ключ для доступа к Object Storage"
  sensitive   = true
}
