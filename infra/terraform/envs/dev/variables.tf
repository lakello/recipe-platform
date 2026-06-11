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
}

variable "redis_password" {
  description = "Пароль для доступа к Redis"
  type        = string
  sensitive   = true
}
