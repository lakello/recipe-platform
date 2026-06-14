resource "yandex_kubernetes_cluster" "this" {
  name        = "${var.environment}-k8s-cluster"
  description = "Основной кластер Managed Kubernetes"
  network_id  = var.vpc_id

  service_account_id      = var.cluster_sa_id
  node_service_account_id = var.node_sa_id

  master {
    version = var.k8s_version

    zonal {
      zone      = var.availability_zones[0]
      subnet_id = var.subnet_ids[0]
    }

    security_group_ids = var.security_group_ids

    public_ip = true
  }
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
