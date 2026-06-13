resource "yandex_dns_zone" "public" {
  name   = trimsuffix(replace(replace(var.zone_name, ".", "-"), "_", "-"), "-")
  zone   = var.zone_name
  public = true
}

resource "yandex_dns_recordset" "subdomains" {
  for_each = toset(var.subdomains)

  zone_id = yandex_dns_zone.public.id
  name    = each.value == "" ? var.zone_name : "${each.value}.${var.zone_name}"
  type    = "A"
  ttl     = var.ttl
  data    = [var.ingress_ip]
}

resource "yandex_dns_recordset" "wildcard" {
  count = var.create_wildcard ? 1 : 0

  zone_id = yandex_dns_zone.public.id
  name    = "*.${var.zone_name}"
  type    = "A"
  ttl     = var.ttl
  data    = [var.ingress_ip]
}
