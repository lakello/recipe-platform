# Модуль iam

Terraform-модуль для централизованного управления сервисными аккаунтами и IAM-правами в Yandex Cloud.

## Что создаёт

| Ресурс | Имя | Роли |
|--------|-----|------|
| SA для кластера K8s | `{env}-k8s-cluster-sa` | `k8s.clusters.agent`, `k8s.tunnelClusters.agent`, `vpc.publicAdmin` |
| SA для нод K8s | `{env}-k8s-node-sa` | `container-registry.images.puller` |
| SA для Object Storage | `{env}-storage-sa` | bucket-scoped `storage.editor` назначается модулем Object Storage |
| SA для push образов | `{env}-image-pusher-sa` | `container-registry.images.pusher` |
| SA для deployment | `{env}-deployer-sa` | доступ к кластеру назначается отдельно от provisioning |

Для `storage-sa` дополнительно создаётся `yandex_iam_service_account_static_access_key` — статический ключ для S3-совместимого доступа к Object Storage.

## Принцип минимальных прав

Кластерный SA, SA нод, runtime storage, image push и deployment разделены. GitHub Actions получает image-pusher и deployer identities через OIDC federation без постоянных CI-ключей.

## Переменные

| Переменная  | Тип    | Описание                          |
|-------------|--------|-----------------------------------|
| `folder_id` | string | ID папки в Yandex Cloud           |
| `env`       | string | Префикс окружения (dev, staging, prod) |
| `github_oidc_audience` | string | Audience GitHub Actions OIDC |
| `github_repository` | string | Репозиторий в формате `owner/name` |

## Outputs

| Output               | Описание                                  |
|----------------------|-------------------------------------------|
| `k8s_cluster_sa_id`  | ID SA для управления кластером K8s        |
| `k8s_node_sa_id`     | ID SA для нод K8s                         |
| `storage_sa_id`      | ID SA для Object Storage                  |
| `image_pusher_sa_id` | ID SA для публикации container images     |
| `deployer_sa_id`     | ID SA для deployment                      |
| `access_key_id`      | Access key ID для Object Storage (S3 API) |
| `secret_access_key`  | Secret key для Object Storage (sensitive) |

## Пример использования

```hcl
module "iam" {
  source               = "../../modules/iam"
  folder_id            = var.folder_id
  env                  = var.environment
  github_oidc_audience = var.github_oidc_audience
  github_repository    = var.github_repository
}

module "kubernetes" {
  source        = "../../modules/kubernetes"
  cluster_sa_id = module.iam.k8s_cluster_sa_id
  node_sa_id    = module.iam.k8s_node_sa_id
  # ...
}

module "object_storage" {
  source        = "../../modules/object-storage"
  storage_sa_id = module.iam.storage_sa_id
  # ...
}
```
