variable "cluster_name" {
  description = "Имя кластера Redis"
  type        = string
}

variable "environment" {
  description = "Окружение (например, production, staging)"
  type        = string
}

variable "network_id" {
  description = "ID сети для размещения кластера"
  type        = string
}

variable "security_group_ids" {
  description = "Список ID групп безопасности"
  type        = list(string)
}

variable "zone" {
  description = "Зона размещения кластера"
  type        = string
}

variable "subnet_id" {
  description = "ID подсети для размещения кластера"
  type        = string
}

variable "redis_password" {
  description = "Пароль для доступа к Redis"
  type        = string
  sensitive   = true
}
