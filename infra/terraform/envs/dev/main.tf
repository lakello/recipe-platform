module "network" {
  source = "../../modules/network"

  environment         = var.environment
  instance_tags       = var.instance_tags
  availability_zones  = var.availability_zones
  public_subnet_cidr  = var.public_subnet_cidr
  private_subnet_cidr = var.private_subnet_cidr
}

module "kubernetes" {
  source = "../../modules/kubernetes"

  environment        = var.environment
  availability_zones = var.availability_zones
  folder_id          = var.folder_id
  k8s_version        = var.k8s_version
  vpc_id             = module.network.vpc_id

  subnet_ids = [
    module.network.public_subnet_id,
    module.network.private_subnet_id,
  ]

  security_group_ids = [
    module.network.public_sg_id,
    module.network.private_sg_id,
    module.network.database_sg_id,
    module.network.kubernetes_sg_id,
  ]
}

module "postgres" {
  source = "../../modules/postgres"

  cluster_name      = "recipe-platform-postgres-${var.environment}"
  environment       = var.environment
  folder_id         = var.folder_id
  database_name     = var.database_name
  database_user     = var.database_user
  database_password = var.database_password
  network_id        = module.network.vpc_id
  zone              = var.availability_zones[1]
  subnet_id         = module.network.private_subnet_id
  security_group_ids = [
    module.network.database_sg_id,
  ]
}

module "redis" {
  source = "../../modules/redis"

  cluster_name = "recipe-platform-redis-${var.environment}"
  environment  = var.environment
  network_id   = module.network.vpc_id
  zone         = var.availability_zones[1]
  subnet_id    = module.network.private_subnet_id
  security_group_ids = [
    module.network.database_sg_id,
  ]
  redis_password = var.redis_password
}

module "object_storage" {
  source = "../../modules/object-storage"

  bucket_config = {
    "recipe-platform-bucket-${var.environment}" = {
      versioning = var.environment == "prod" ? true : false
    }
  }
  access_key = var.service_access_id
  secret_key = var.service_access_key
  folder_id  = var.folder_id
}
