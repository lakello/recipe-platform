variable "folder_id" {
  description = "ID каталога в Yandex Cloud, где будут созданы SA и назначены роли"
  type        = string
}

variable "env" {
  description = "Префикс окружения для именования (например: dev, stage, prod)"
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
