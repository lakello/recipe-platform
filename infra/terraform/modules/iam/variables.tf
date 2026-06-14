variable "folder_id" {
  description = "ID каталога в Yandex Cloud, где будут созданы SA и назначены роли"
  type        = string
}

variable "env" {
  description = "Префикс окружения для именования (например: dev, stage, prod)"
  type        = string
}
