resource "yandex_storage_bucket" "bucket" {
  for_each = var.bucket_config

  bucket     = each.key
  access_key = var.access_key
  secret_key = var.secret_key
  versioning {
    enabled = each.value.versioning
  }

  lifecycle_rule {
    id      = "abort-incomplete-multipart-uploads"
    enabled = true

    abort_incomplete_multipart_upload_days = 7
  }

  lifecycle_rule {
    id      = "cleanup-old-versions"
    enabled = true

    noncurrent_version_expiration {
      days = 30
    }
  }

  cors_rule {
    allowed_origins = var.allowed_origins

    allowed_methods = ["PUT", "POST", "GET"]

    allowed_headers = ["*"]

    expose_headers = ["ETag", "Content-Length", "Connection"]

    max_age_seconds = 3000
  }
}

resource "yandex_iam_service_account" "service_account" {
  name        = "object-storage-service-account"
  description = "Service account for Object Storage access"
}

resource "yandex_resourcemanager_folder_iam_member" "folder_member" {
  folder_id = var.folder_id
  role      = "storage.editor"
  member    = "serviceAccount:${yandex_iam_service_account.service_account.id}"
}

resource "yandex_iam_service_account_static_access_key" "access_key" {
  service_account_id = yandex_iam_service_account.service_account.id
  description        = "Static access key for Object Storage"
}
