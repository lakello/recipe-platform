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
