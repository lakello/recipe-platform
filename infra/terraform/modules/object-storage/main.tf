resource "yandex_storage_bucket" "bucket" {
  for_each = var.bucket_config

  bucket = each.key

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

resource "yandex_storage_bucket_iam_binding" "bucket_iam" {
  for_each = yandex_storage_bucket.bucket

  bucket  = yandex_storage_bucket.bucket[each.key].id
  role    = "storage.editor"
  members = ["serviceAccount:${var.storage_sa_id}"]
}
