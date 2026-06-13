variable "zone" {
  description = "Зона доступности для развертывания инстанса"
  type        = string
  default     = "ru-central1-a"
}

variable "network_id" {
  description = "ID сети VPC, в которой создается группа безопасности"
  type        = string
}

variable "subnet_id" {
  description = "ID публичной подсети для размещения инстанса"
  type        = string
}

variable "image_id" {
  description = "ID образа операционной системы (например, Ubuntu)"
  type        = string
}

variable "ssh_user" {
  description = "Имя пользователя для SSH-доступа"
  type        = string
  default     = "ubuntu"
}

variable "ssh_public_key" {
  description = "Публичный SSH-ключ для авторизации"
  type        = string
}

variable "allowed_ssh_cidr" {
  description = "CIDR-блок (ваш IP), которому разрешен доступ по SSH"
  type        = string
}
