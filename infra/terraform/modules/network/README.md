# Модуль network

Terraform-модуль для создания сетевой инфраструктуры в Yandex Cloud.

## Что создаёт модуль

- **VPC network** — основная сеть окружения
- **Public subnet** — для внешних точек входа (load balancer, bastion)
- **Private subnet** — для внутренних ресурсов (Kubernetes nodes, БД, Redis)
- **Egress gateway** — NAT-шлюз для выхода приватных ресурсов в интернет
- **Route table** — маршрут `0.0.0.0/0` через egress gateway, привязан к private subnet
- **Security groups**:
  - `ingress_sg` — разрешает входящий HTTP (80) и HTTPS (443) из интернета
  - `control_plane_sg` — ограничивает доступ к Kubernetes API значением `admin_cidr`
  - `nodes_sg` — разрешает kubelet и внутренний обмен между нодами без публичного NodePort
  - `postgresql_sg` — разрешает PostgreSQL (5432) только из `nodes_sg`
  - `redis_sg` — разрешает Redis (6379) только из `nodes_sg`

## Переменные

| Переменная           | Тип          | Описание                          |
|----------------------|--------------|-----------------------------------|
| `environment`        | string       | Название окружения (dev, staging) |
| `instance_tags`      | map(string)  | Labels для всех ресурсов          |
| `availability_zones` | list(string) | Зоны доступности                  |
| `public_subnet_cidr` | string       | CIDR публичной подсети            |
| `private_subnet_cidr`| string       | CIDR приватной подсети            |
| `admin_cidr`         | string       | CIDR для административного доступа|
| `cluster_ipv4_range` | string       | CIDR pod-сети Kubernetes          |

## Outputs

| Output            | Описание                        |
|-------------------|---------------------------------|
| `vpc_id`          | ID VPC сети                     |
| `public_subnet_id`| ID публичной подсети            |
| `private_subnet_id`| ID приватной подсети           |
| `ingress_sg_id`   | ID security group для ingress   |
| `control_plane_sg_id` | ID security group control plane |
| `nodes_sg_id`     | ID security group worker nodes  |
| `postgresql_sg_id`| ID security group PostgreSQL    |
| `redis_sg_id`     | ID security group Redis         |

## Использование

```hcl
module "network" {
  source = "../../modules/network"

  environment           = var.environment
  instance_tags         = var.instance_tags
  availability_zones    = var.availability_zones
  public_subnet_cidr    = var.public_subnet_cidr
  private_subnet_cidr   = var.private_subnet_cidr
  admin_cidr            = var.admin_cidr
  cluster_ipv4_range    = var.cluster_ipv4_range
}
```
