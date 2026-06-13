variable "cluster_name" {
  description = "Имя кластера PostgreSQL"
  type        = string
}

variable "environment" {
  description = "Окружение (например, production, staging)"
  type        = string
}

variable "folder_id" {
  description = "ID папки в Яндекс.Облаке"
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
