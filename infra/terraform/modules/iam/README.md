# Модуль iam

Terraform-модуль для централизованного управления сервисными аккаунтами и IAM-правами в Yandex Cloud.

## Что создаёт

| Ресурс | Имя | Роли |
|--------|-----|------|
| SA для кластера K8s | `{env}-k8s-cluster-sa` | `k8s.clusters.agent`, `k8s.tunnelClusters.agent`, `vpc.publicAdmin` |
| SA для нод K8s | `{env}-k8s-node-sa` | `container-registry.images.puller` |
| SA для Object Storage | `{env}-storage-sa` | `storage.editor` |
| SA для CI/CD | `{env}-cicd-sa` | `container-registry.images.pusher`, `k8s.cluster-api.cluster-admin` |

Для `storage-sa` дополнительно создаётся `yandex_iam_service_account_static_access_key` — статический ключ для S3-совместимого доступа к Object Storage.

## Принцип минимальных прав

Кластерный SA и SA нод разделены намеренно: ноды не имеют прав `vpc.publicAdmin` — только доступ к Container Registry для pull образов.

## Переменные

| Переменная  | Тип    | Описание                          |
|-------------|--------|-----------------------------------|
| `folder_id` | string | ID папки в Yandex Cloud           |
| `env`       | string | Префикс окружения (dev, stage, prod) |

## Outputs

| Output               | Описание                                  |
|----------------------|-------------------------------------------|
| `k8s_cluster_sa_id`  | ID SA для управления кластером K8s        |
| `k8s_node_sa_id`     | ID SA для нод K8s                         |
| `storage_sa_id`      | ID SA для Object Storage                  |
| `cicd_sa_id`         | ID SA для CI/CD pipeline                  |
| `access_key_id`      | Access key ID для Object Storage (S3 API) |
| `secret_access_key`  | Secret key для Object Storage (sensitive) |

## Пример использования

```hcl
module "iam" {
  source    = "../../modules/iam"
  folder_id = var.folder_id
  env       = var.environment
}

module "kubernetes" {
  source        = "../../modules/kubernetes"
  cluster_sa_id = module.iam.k8s_cluster_sa_id
  node_sa_id    = module.iam.k8s_node_sa_id
  # ...
}

module "object_storage" {
  source     = "../../modules/object-storage"
  access_key = module.iam.access_key_id
  secret_key = module.iam.secret_access_key
  # ...
}
```
