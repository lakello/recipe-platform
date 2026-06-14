# Модуль kubernetes

Terraform-модуль для создания Managed Kubernetes кластера в Yandex Cloud.

## Что создаёт модуль

- **Kubernetes cluster** — Managed Kubernetes с публичным endpoint у master
- **Node group `system`** — фиксированные 2 ноды для системных компонентов (Ingress, CoreDNS), taint `CriticalAddonsOnly=true:NoSchedule`
- **Node group `app`** — автоскейлинг-группа для приложений (backend, frontend, workers), preemptible в non-prod

Сервисные аккаунты создаются вне модуля — в `modules/iam` — и передаются через переменные `cluster_sa_id` и `node_sa_id`.

## Размещение нод

Все worker nodes размещаются в **private subnet** — прямой доступ из интернета закрыт. Выход в интернет (для скачивания образов) — через NAT gateway из модуля `network`.

## Переменные

| Переменная            | Тип          | Описание                                        | Дефолт         |
|-----------------------|--------------|-------------------------------------------------|----------------|
| `environment`         | string       | Название окружения                              | `"dev"`        |
| `cluster_sa_id`       | string       | ID SA для управления кластером (из модуля iam)  | —              |
| `node_sa_id`          | string       | ID SA для нод (из модуля iam)                   | —              |
| `k8s_version`         | string       | Версия Kubernetes                               | `"1.33"`       |
| `vpc_id`              | string       | ID VPC сети                                     | —              |
| `subnet_ids`          | list(string) | IDs подсетей (index 0 — public, 1 — private)    | —              |
| `security_group_ids`  | list(string) | IDs security groups                             | —              |
| `availability_zones`  | list(string) | Зоны доступности                                | —              |
| `node_platform_id`    | string       | Тип платформы процессора                        | `"standard-v3"`|
| `node_cores`          | number       | vCPU на ноду                                    | `4`            |
| `node_memory`         | number       | RAM в ГБ на ноду                                | `8`            |
| `node_disk_type`      | string       | Тип диска                                       | `"network-hdd"`|
| `node_disk_size`      | number       | Размер диска в ГБ                               | `30`           |
| `autoscaling_config`  | object       | min/max/initial nodes для app node group        | 2/10/2         |

## Outputs

| Output                 | Описание                              |
|------------------------|---------------------------------------|
| `cluster_id`           | ID кластера                           |
| `cluster_name`         | Имя кластера                          |
| `system_node_group_id` | ID node group system                  |
| `app_node_group_id`    | ID node group app                     |

## Использование

```hcl
module "kubernetes" {
  source             = "../../modules/kubernetes"
  environment        = var.environment
  k8s_version        = var.k8s_version
  availability_zones = var.availability_zones
  vpc_id             = module.network.vpc_id
  cluster_sa_id      = module.iam.k8s_cluster_sa_id
  node_sa_id         = module.iam.k8s_node_sa_id

  subnet_ids = [
    module.network.public_subnet_id,
    module.network.private_subnet_id,
  ]

  security_group_ids = [
    module.network.public_sg_id,
    module.network.private_sg_id,
    module.network.database_sg_id,
    module.network.kubernetes_sg_id,
  ]
}
```

## Получение kubeconfig

```bash
yc managed-kubernetes cluster get-credentials \
  --id <cluster_id> \
  --external \
  --kubeconfig kubeconfig
```
