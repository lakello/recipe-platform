variable "cloud_id" {
  description = "ID облака в Yandex.Cloud"
  type        = string
}

variable "folder_id" {
  description = "ID папки в Yandex.Cloud"
  type        = string
}

variable "environment" {
  description = "Название окружения"
  type        = string

  validation {
    condition     = length(var.environment) > 0
    error_message = "Название окружения не может быть пустым"
  }

  validation {
    condition     = var.environment == "prod" || var.environment == "staging" || var.environment == "dev"
    error_message = "Название окружения должно быть 'prod', 'staging' или 'dev'"
  }
}

variable "instance_tags" {
  description = "Теги для экземпляров"
  type        = map(string)
}

variable "availability_zones" {
  description = "Зоны доступности"
  type        = list(string)

  validation {
    condition     = length(var.availability_zones) > 1
    error_message = "Список зон доступности должен содержать как минимум две зоны"
  }
}

variable "public_subnet_cidr" {
  description = "CIDR блок для публичной подсети"
  type        = string
}

variable "private_subnet_cidr" {
  description = "CIDR блок для приватной подсети"
  type        = string
}

variable "k8s_version" {
  description = "Версия Kubernetes"
  type        = string
}

variable "database_name" {
  description = "Имя базы данных"
  type        = string
}

variable "database_user" {
  description = "Имя пользователя базы данных"
  type        = string
}

variable "database_password" {
  description = "Пароль пользователя базы данных"
  type        = string
  sensitive   = true

  validation {
    condition     = length(var.database_password) >= 8
    error_message = "Пароль пользователя базы данных должен быть не менее 8 символов"
  }
}

variable "redis_password" {
  description = "Пароль для доступа к Redis"
  type        = string
  sensitive   = true

  validation {
    condition     = length(var.redis_password) >= 8
    error_message = "Пароль для доступа к Redis должен быть не менее 8 символов"
  }
}

variable "admin_cidr" {
  description = "CIDR-блок, которому разрешен доступ по SSH и Kubernetes API"
  type        = string
}

variable "ssh_public_key" {
  description = "Публичный ключ SSH"
  type        = string

  validation {
    condition     = length(var.ssh_public_key) > 0
    error_message = "Публичный ключ SSH не может быть пустым"
  }
}

variable "dns_zone_name" {
  description = "Имя DNS-зоны"
  type        = string
}

variable "cluster_ipv4_range" {
  description = "CIDR блок для кластера Kubernetes"
  type        = string
}

variable "github_oidc_audience" {
  description = "Audience для GitHub Actions OIDC"
  type        = string
}

variable "github_repository" {
  description = "GitHub repository в формате owner/name"
  type        = string
}