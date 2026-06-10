module "network" {
  source              = "../../modules/network"
  environment         = var.environment
  instance_tags       = var.instance_tags
  availability_zones  = var.availability_zones
  public_subnet_cidr  = var.public_subnet_cidr
  private_subnet_cidr = var.private_subnet_cidr
}
