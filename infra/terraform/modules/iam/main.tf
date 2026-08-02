# Сервисный аккаунт для управления кластером Kubernetes
resource "yandex_iam_service_account" "k8s_cluster" {
  folder_id = var.folder_id
  name      = "${var.env}-k8s-cluster-sa"
}

resource "yandex_resourcemanager_folder_iam_member" "k8s_cluster_roles" {
  for_each  = toset(["k8s.clusters.agent", "k8s.tunnelClusters.agent", "vpc.publicAdmin"])
  folder_id = var.folder_id
  role      = each.value
  member    = "serviceAccount:${yandex_iam_service_account.k8s_cluster.id}"
}

# Сервисный аккаунт для узлов (nodes) Kubernetes
resource "yandex_iam_service_account" "k8s_node" {
  folder_id = var.folder_id
  name      = "${var.env}-k8s-node-sa"
}

resource "yandex_resourcemanager_folder_iam_member" "k8s_node_roles" {
  for_each  = toset(["container-registry.images.puller"])
  folder_id = var.folder_id
  role      = each.value
  member    = "serviceAccount:${yandex_iam_service_account.k8s_node.id}"
}

# Сервисный аккаунт для работы с Object Storage
resource "yandex_iam_service_account" "storage" {
  folder_id = var.folder_id
  name      = "${var.env}-storage-sa"
}

resource "yandex_iam_service_account_static_access_key" "sa_static_storage_access" {
  service_account_id = yandex_iam_service_account.storage.id
}

# Сервисный аккаунт для CI/CD автоматизации
resource "yandex_iam_service_account" "image_pusher" {
  folder_id = var.folder_id
  name      = "${var.env}-image-pusher-sa"
}

resource "yandex_resourcemanager_folder_iam_member" "image_pusher_roles" {
  folder_id = var.folder_id
  role      = "container-registry.images.pusher"
  member    = "serviceAccount:${yandex_iam_service_account.image_pusher.id}"
}

resource "yandex_iam_service_account" "deployer" {
  folder_id = var.folder_id
  name      = "${var.env}-deployer-sa"
}

resource "yandex_iam_workload_identity_oidc_federation" "github" {
  folder_id = var.folder_id
  name      = "${var.env}-github-actions"

  issuer    = "https://token.actions.githubusercontent.com"
  audiences = [var.github_oidc_audience]
  jwks_url  = "https://token.actions.githubusercontent.com/.well-known/jwks"
}

resource "yandex_iam_workload_identity_federated_credential" "image_pusher" {
  service_account_id  = yandex_iam_service_account.image_pusher.id
  federation_id       = yandex_iam_workload_identity_oidc_federation.github.id
  external_subject_id = "repo:${var.github_repository}:environment:${var.env}-build"
}

resource "yandex_iam_workload_identity_federated_credential" "deployer" {
  service_account_id  = yandex_iam_service_account.deployer.id
  federation_id       = yandex_iam_workload_identity_oidc_federation.github.id
  external_subject_id = "repo:${var.github_repository}:environment:${var.env}"
}