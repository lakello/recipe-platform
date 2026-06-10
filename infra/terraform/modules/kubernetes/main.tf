resource "yandex_iam_service_account" "k8s_sa" {
  name        = "${var.environment}-k8s-sa"
  description = "Сервисный аккаунт для управления кластером и нодами K8s"
}

resource "yandex_resourcemanager_folder_iam_member" "k8s_roles" {
  for_each = toset([
    "k8s.clusters.agent",
    "k8s.tunnelClusters.agent",
    "vpc.publicAdmin",
    "container-registry.images.puller"
  ])

  folder_id = var.folder_id
  role      = each.value
  member    = "serviceAccount:${yandex_iam_service_account.k8s_sa.id}"
}



resource "yandex_kubernetes_cluster" "this" {
  name        = "${var.environment}-k8s-cluster"
  description = "Основной кластер Managed Kubernetes"
  network_id  = var.vpc_id

  service_account_id      = yandex_iam_service_account.k8s_sa.id
  node_service_account_id = yandex_iam_service_account.k8s_sa.id

  master {
    version = var.k8s_version

    zonal {
      zone      = var.availability_zones[0]
      subnet_id = var.subnet_ids[0]
    }

    security_group_ids = var.security_group_ids

    public_ip = true
  }

  depends_on = [
    yandex_resourcemanager_folder_iam_member.k8s_roles
  ]
}



resource "yandex_kubernetes_node_group" "system" {
  cluster_id  = yandex_kubernetes_cluster.this.id
  name        = "${var.environment}-ng-system"
  description = "Группа узлов для системных сервисов (Ingress, CoreDNS, Тейнты)"
  version     = var.k8s_version

  instance_template {
    platform_id = var.node_platform_id

    resources {
      cores  = var.node_cores
      memory = var.node_memory
    }

    boot_disk {
      type = var.node_disk_type
      size = var.node_disk_size
    }

    network_interface {
      nat                = false
      subnet_ids         = [var.subnet_ids[1]]
      security_group_ids = var.security_group_ids
    }

    scheduling_policy {
      preemptible = false
    }
  }

  scale_policy {
    fixed_scale {
      size = 2
    }
  }

  node_taints = ["CriticalAddonsOnly=true:NoSchedule"]

  labels = {
    role = "system"
  }
}



resource "yandex_kubernetes_node_group" "app" {
  cluster_id  = yandex_kubernetes_cluster.this.id
  name        = "${var.environment}-ng-app"
  description = "Группа узлов для размещения пользовательских приложений"
  version     = var.k8s_version

  instance_template {
    platform_id = var.node_platform_id

    resources {
      cores  = var.node_cores
      memory = var.node_memory
    }

    boot_disk {
      type = var.node_disk_type
      size = var.node_disk_size
    }

    network_interface {
      nat                = false
      subnet_ids         = [var.subnet_ids[1]]
      security_group_ids = var.security_group_ids
    }

    scheduling_policy {
      preemptible = var.environment == "prod" ? false : true
    }
  }

  scale_policy {
    auto_scale {
      min     = var.autoscaling_config.min_nodes
      max     = var.autoscaling_config.max_nodes
      initial = var.autoscaling_config.initial_nodes
    }
  }

  labels = {
    role = "apps"
  }
}
