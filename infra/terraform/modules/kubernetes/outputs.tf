output "cluster_id" {
  value       = yandex_kubernetes_cluster.this.id
  description = "Идентификатор созданного кластера Kubernetes"
}

output "cluster_name" {
  value       = yandex_kubernetes_cluster.this.name
  description = "Имя созданного кластера Kubernetes"
}

output "system_node_group_id" {
  value       = yandex_kubernetes_node_group.system.id
  description = "Идентификатор созданной системной группы узлов Kubernetes"
}

output "app_node_group_id" {
  value       = yandex_kubernetes_node_group.app.id
  description = "Идентификатор созданной группы узлов для приложений Kubernetes"
}
