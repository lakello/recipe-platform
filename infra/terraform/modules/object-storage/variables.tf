variable "bucket_config" {
  description = "Конфигурация для создания бакетов в Yandex Object Storage"
  type = map(object({
    versioning = bool
  }))
}

variable "access_key" {
  description = "Access key для доступа к Yandex Object Storage"
  type        = string
}

variable "secret_key" {
  description = "Secret key для доступа к Yandex Object Storage"
  type        = string
  sensitive   = true
}

variable "folder_id" {
  description = "ID папки в Yandex Cloud для назначения прав доступа"
  type        = string
}

variable "allowed_origins" {
  description = "Список разрешенных источников для CORS"
  type        = list(string)
  default     = ["http://localhost:3000"]
}
