output "instance_id" {
  description = "ID созданного инстанса"
  value       = yandex_compute_instance.bastion.id
}

output "public_ip" {
  description = "Статический публичный IP-адрес (для Ansible-инвентаря)"
  value       = yandex_compute_instance.bastion.network_interface[0].nat_ip_address
}

output "internal_ip" {
  description = "Внутренний IP-адрес инстанса"
  value       = yandex_compute_instance.bastion.network_interface[0].ip_address
}
