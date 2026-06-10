module "network" {
  source              = "../../modules/network"
  environment         = var.environment
  instance_tags       = var.instance_tags
  availability_zones  = var.availability_zones
  public_subnet_cidr  = var.public_subnet_cidr
  private_subnet_cidr = var.private_subnet_cidr
}

module "kubernetes" {
  source             = "../../modules/kubernetes"
  environment        = var.environment
  availability_zones = var.availability_zones
  folder_id          = var.folder_id
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
