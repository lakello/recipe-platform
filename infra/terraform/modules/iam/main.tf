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

resource "yandex_resourcemanager_folder_iam_member" "storage_roles" {
  for_each  = toset(["storage.editor"])
  folder_id = var.folder_id
  role      = each.value
  member    = "serviceAccount:${yandex_iam_service_account.storage.id}"
}

resource "yandex_iam_service_account_static_access_key" "sa_static_storage_access" {
  service_account_id = yandex_iam_service_account.storage.id
}

# Сервисный аккаунт для CI/CD автоматизации
resource "yandex_iam_service_account" "cicd" {
  folder_id = var.folder_id
  name      = "${var.env}-cicd-sa"
}

resource "yandex_resourcemanager_folder_iam_member" "cicd_roles" {
  for_each  = toset(["container-registry.images.pusher", "k8s.cluster-api.cluster-admin"])
  folder_id = var.folder_id
  role      = each.value
  member    = "serviceAccount:${yandex_iam_service_account.cicd.id}"
}
