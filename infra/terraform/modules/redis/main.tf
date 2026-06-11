resource "yandex_mdb_redis_cluster" "redis" {
  name                = var.cluster_name
  environment         = var.environment == "prod" ? "PRODUCTION" : "PRESTABLE"
  network_id          = var.network_id
  security_group_ids  = var.security_group_ids
  deletion_protection = var.environment == "prod" ? true : false
  persistence_mode    = var.environment == "prod" ? "ON" : "OFF"

  config {
    version          = "6.2"
    password         = var.redis_password
    maxmemory_policy = "ALLKEYS_LRU"
  }

  resources {
    resource_preset_id = "hm1.nano"
    disk_size          = 16
    disk_type_id       = "network-ssd"
  }

  host {
    zone      = var.zone
    subnet_id = var.subnet_id
  }
}
