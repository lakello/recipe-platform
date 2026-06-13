terraform {
  required_providers {
    yandex = {
      source  = "yandex-cloud/yandex"
      version = "~> 0.206"
    }
  }
}

provider "yandex" {
  service_account_key_file = "authorized_key.json" # pragma: allowlist secret
  cloud_id                 = var.cloud_id
  folder_id                = var.folder_id
}
