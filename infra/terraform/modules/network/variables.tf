variable "environment" {
  description = "Название окружения"
  type        = string
}

variable "instance_tags" {
  description = "Теги для экземпляров"
  type        = map(string)
}

variable "availability_zones" {
  description = "Зоны доступности"
  type        = list(string)
}

variable "public_subnet_cidr" {
  description = "CIDR блок для публичной подсети (например, 10.10.1.0/24)"
  type        = string

  validation {
    condition     = can(cidrnetmask(var.public_subnet_cidr))
    error_message = "Недопустимый CIDR блок для публичной подсети"
  }
}

variable "private_subnet_cidr" {
  description = "CIDR блок для приватной подсети (например, 10.10.2.0/24)"
  type        = string

  validation {
    condition     = can(cidrnetmask(var.private_subnet_cidr))
    error_message = "Недопустимый CIDR блок для приватной подсети"
  }
}

variable "admin_cidr" {
  description = "CIDR-блок, которому разрешен доступ по SSH и Kubernetes API"
  type        = string

  validation {
    condition     = can(cidrnetmask(var.admin_cidr))
    error_message = "Недопустимый CIDR блок для доступа по SSH и Kubernetes API"
  }

  validation {
    condition     = length(var.admin_cidr) > 0
    error_message = "CIDR блок для доступа по SSH и Kubernetes API не может быть пустым"
  }

  validation {
    condition     = var.admin_cidr != "0.0.0.0/0"
    error_message = "CIDR блок для доступа по SSH и Kubernetes API не может быть '0.0.0.0/0'"
  }
}

variable "cluster_ipv4_range" {
  description = "CIDR блок для кластера Kubernetes"
  type        = string

  validation {
    condition     = can(cidrnetmask(var.cluster_ipv4_range))
    error_message = "Недопустимый CIDR блок для кластера Kubernetes"
  }
}