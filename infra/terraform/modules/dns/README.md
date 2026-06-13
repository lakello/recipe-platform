# Модуль dns

Terraform-модуль для создания публичной DNS-зоны и A-записей в Yandex Cloud DNS.

## Что создаёт модуль

- `yandex_dns_zone` — публичная DNS-зона
- `yandex_dns_recordset` (через `for_each`) — A-записи для apex и поддоменов, все указывают на один IP
- `yandex_dns_recordset` (wildcard, опционально) — запись `*.example.com` для любых поддоменов

## Назначение

Модуль управляет DNS-записями проекта через Terraform. Все домены указывают на IP Kubernetes Ingress / Load Balancer.

После `terraform apply` нужно делегировать домен на NS-серверы Yandex Cloud у регистратора. NS-серверы возвращаются в output `name_servers`.

## Использование

```hcl
module "dns" {
  source = "../../modules/dns"

  zone_name  = var.dns_zone_name   # "example.com."
  ingress_ip = var.ingress_ip      # IP Kubernetes Ingress

  subdomains      = ["", "dev", "staging", "api", "grafana"]
  create_wildcard = true
}
```

## Переменные

| Переменная       | Тип          | По умолчанию                            | Описание                                         |
|------------------|--------------|-----------------------------------------|--------------------------------------------------|
| `zone_name`      | string       | —                                       | FQDN зоны с точкой на конце (`example.com.`)     |
| `ingress_ip`     | string       | —                                       | IP-адрес Ingress / Load Balancer                 |
| `subdomains`     | list(string) | `["", "dev", "staging", "api", "grafana"]` | Поддомены; `""` — apex-запись (`example.com`) |
| `create_wildcard`| bool         | `true`                                  | Создавать ли запись `*.example.com`              |
| `ttl`            | number       | `300`                                   | TTL записей в секундах                           |

## Outputs

| Output         | Описание                                                          |
|----------------|-------------------------------------------------------------------|
| `zone_id`      | ID созданной DNS-зоны                                             |
| `name_servers` | NS-серверы для делегирования (`ns1/ns2.yandexcloud.net.`)         |

## Делегирование домена

После применения Terraform нужно прописать у регистратора домена:

```
ns1.yandexcloud.net.
ns2.yandexcloud.net.
```

## Структура

```
modules/dns/
  main.tf        # yandex_dns_zone, yandex_dns_recordset
  variables.tf   # входные переменные
  outputs.tf     # zone_id, name_servers
  providers.tf   # required_providers
```
