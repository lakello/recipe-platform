output "zone_id" {
  description = "ID созданной DNS-зоны"
  value       = yandex_dns_zone.public.id
}

output "name_servers" {
  description = "NS-серверы для делегирования домена у регистратора"
  value       = ["ns1.yandexcloud.net.", "ns2.yandexcloud.net."]
}
