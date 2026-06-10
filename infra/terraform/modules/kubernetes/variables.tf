variable "environment" {
  type        = string
  description = "Название окружения (например: dev, stage, prod)"
  default     = "dev"
}

variable "k8s_version" {
  type        = string
  description = "Версия Kubernetes для кластера и групп узлов"
  default     = "1.28"
}



variable "vpc_id" {
  type        = string
  description = "ID созданной VPC сети"
}

variable "subnet_ids" {
  type        = list(string)
  description = "Список ID подсетей для размещения узлов (нод) кластера"
}

variable "security_group_ids" {
  type        = list(string)
  description = "Список ID групп безопасности (включая internal и database SG)"
}

variable "node_platform_id" {
  type        = string
  description = "Тип платформы процессора (например: standard-v3, intel-ice-lake)"
  default     = "standard-v3"
}

variable "node_cores" {
  type        = number
  description = "Количество ядер (vCPU) на одну ноду"
  default     = 4
}

variable "node_memory" {
  type        = number
  description = "Объем оперативной памяти (RAM) в ГБ на одну ноду"
  default     = 8
}

variable "node_disk_type" {
  type        = string
  description = "Тип диска для нод (network-ssd для скорости, network-hdd для экономии)"
  default     = "network-ssd"
}

variable "node_disk_size" {
  type        = number
  description = "Размер диска ноды в гигабайтах"
  default     = 64
}



variable "autoscaling_config" {
  type = object({
    min_nodes     = number
    max_nodes     = number
    initial_nodes = number
  })
  description = "Параметры автоскейлинга для группы узлов"
  default = {
    min_nodes     = 2
    max_nodes     = 10
    initial_nodes = 2
  }
}



variable "folder_id" {
  type        = string
  description = "ID папки в Yandex.Cloud, где будет создан кластер"
}

variable "availability_zones" {
  description = "Зоны доступности"
  type        = list(string)
}
