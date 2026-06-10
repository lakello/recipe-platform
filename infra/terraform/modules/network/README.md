# Модуль network

Terraform-модуль для создания сетевой инфраструктуры в Yandex Cloud.

## Что создаёт модуль

- **VPC network** — основная сеть окружения
- **Public subnet** — для внешних точек входа (load balancer, bastion)
- **Private subnet** — для внутренних ресурсов (Kubernetes nodes, БД, Redis)
- **Egress gateway** — NAT-шлюз для выхода приватных ресурсов в интернет
- **Route table** — маршрут `0.0.0.0/0` через egress gateway, привязан к private subnet
- **Security groups**:
  - `public_sg` — разрешает входящий HTTP (80) и HTTPS (443) из интернета
  - `private_sg` — разрешает внутренний трафик внутри VPC
  - `database_sg` — разрешает доступ к PostgreSQL (5432) и Redis (6379) только из `private_sg`
  - `kubernetes_sg` — правила для Kubernetes нод: API server (443), kubelet (10250), NodePort (30000–32767), ICMP, node-to-node трафик

## Переменные

| Переменная           | Тип          | Описание                          |
|----------------------|--------------|-----------------------------------|
| `environment`        | string       | Название окружения (dev, staging) |
| `instance_tags`      | map(string)  | Labels для всех ресурсов          |
| `availability_zones` | list(string) | Зоны доступности                  |
| `public_subnet_cidr` | string       | CIDR публичной подсети            |
| `private_subnet_cidr`| string       | CIDR приватной подсети            |

## Outputs

| Output            | Описание                        |
|-------------------|---------------------------------|
| `vpc_id`          | ID VPC сети                     |
| `public_subnet_id`| ID публичной подсети            |
| `private_subnet_id`| ID приватной подсети           |
| `public_sg_id`    | ID публичной security group     |
| `private_sg_id`   | ID приватной security group     |
| `database_sg_id`  | ID security group для БД        |
| `kubernetes_sg_id`| ID security group для Kubernetes|

## Использование

```hcl
module "network" {
  source = "../../modules/network"

  environment           = var.environment
  instance_tags         = var.instance_tags
  availability_zones    = var.availability_zones
  public_subnet_cidr    = var.public_subnet_cidr
  private_subnet_cidr   = var.private_subnet_cidr
}
```
