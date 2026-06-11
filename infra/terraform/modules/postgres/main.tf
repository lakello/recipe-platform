resource "yandex_mdb_postgresql_cluster" "postgres" {
  name                = var.cluster_name
  environment         = var.environment == "prod" ? "PRODUCTION" : "PRESTABLE"
  folder_id           = var.folder_id
  network_id          = var.network_id
  security_group_ids  = var.security_group_ids
  deletion_protection = var.environment == "prod" ? true : false

  config {
    version = "15"
    resources {
      resource_preset_id = "s2.micro"
      disk_size          = 16
      disk_type_id       = "network-ssd"
    }
    backup_window_start {
      hours = 3
    }
    backup_retain_period_days = 7
    postgresql_config = {
      max_connections                = 100
      enable_parallel_hash           = true
      autovacuum_vacuum_scale_factor = 0.34
      default_transaction_isolation  = "TRANSACTION_ISOLATION_READ_COMMITTED"
      shared_preload_libraries       = "SHARED_PRELOAD_LIBRARIES_AUTO_EXPLAIN,SHARED_PRELOAD_LIBRARIES_PG_HINT_PLAN"
    }
  }

  host {
    zone      = var.zone
    subnet_id = var.subnet_id
  }

  maintenance_window {
    day  = "SAT"
    hour = 12
    type = "WEEKLY"
  }
}

resource "yandex_mdb_postgresql_database" "database" {
  cluster_id = yandex_mdb_postgresql_cluster.postgres.id
  name       = var.database_name
  owner      = var.database_user
}

resource "yandex_mdb_postgresql_user" "user" {
  cluster_id = yandex_mdb_postgresql_cluster.postgres.id
  name       = var.database_user
  password   = var.database_password
}
