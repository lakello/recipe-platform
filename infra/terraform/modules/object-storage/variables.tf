variable "bucket_config" {
  description = "Конфигурация для создания бакетов в Yandex Object Storage"
  type = map(object({
    versioning = bool
  }))
}

variable "storage_sa_id" {
  description = "ID сервисного аккаунта для доступа к Yandex Object Storage"
  type        = string
}

variable "allowed_origins" {
  description = "Список разрешенных источников для CORS"
  type        = list(string)
  default     = ["http://localhost:3000"]
}
