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
}

variable "private_subnet_cidr" {
  description = "CIDR блок для приватной подсети (например, 10.10.2.0/24)"
  type        = string
}
