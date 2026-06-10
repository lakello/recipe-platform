
resource "yandex_vpc_network" "this" {
  name        = "${var.environment}-vpc"
  description = "Основная сеть для окружения ${var.environment}"

  labels = var.instance_tags
}

resource "yandex_vpc_gateway" "gateway" {
  name        = "${var.environment}-vpc-gateway"
  description = "Публичный шлюз для доступа к сети ${var.environment}"
  shared_egress_gateway {}

  labels = var.instance_tags
}

resource "yandex_vpc_route_table" "route_table" {
  network_id = yandex_vpc_network.this.id

  static_route {
    destination_prefix = "0.0.0.0/0"
    gateway_id         = yandex_vpc_gateway.gateway.id
  }
}

resource "yandex_vpc_subnet" "public_subnet" {
  name           = "${var.environment}-public-subnet"
  description    = "Публичная подсеть в зоне доступности A"
  zone           = var.availability_zones[0]
  network_id     = yandex_vpc_network.this.id
  v4_cidr_blocks = [var.public_subnet_cidr]

  labels = var.instance_tags
}

resource "yandex_vpc_subnet" "private_subnet" {
  name           = "${var.environment}-private-subnet"
  description    = "Приватная подсеть в зоне доступности B"
  zone           = var.availability_zones[1]
  network_id     = yandex_vpc_network.this.id
  v4_cidr_blocks = [var.private_subnet_cidr]
  route_table_id = yandex_vpc_route_table.route_table.id

  labels = var.instance_tags
}

resource "yandex_vpc_security_group" "public_sg" {
  name        = "${var.environment}-public-sg"
  description = "Публичная группа безопасности для окружения ${var.environment}"
  network_id  = yandex_vpc_network.this.id

  labels = var.instance_tags

  egress {
    protocol       = "ANY"
    v4_cidr_blocks = ["0.0.0.0/0"]
    from_port      = 0
    to_port        = 65535
  }

  ingress {
    protocol       = "TCP"
    description    = "Входящий HTTP трафик"
    v4_cidr_blocks = ["0.0.0.0/0"]
    port           = 80
  }

  ingress {
    protocol       = "TCP"
    description    = "Входящий HTTPS трафик"
    v4_cidr_blocks = ["0.0.0.0/0"]
    port           = 443
  }
}

resource "yandex_vpc_security_group" "private_sg" {
  name        = "${var.environment}-private-sg"
  description = "Приватная группа безопасности для окружения ${var.environment}"
  network_id  = yandex_vpc_network.this.id

  labels = var.instance_tags

  egress {
    protocol       = "ANY"
    description    = "Исходящий трафик"
    v4_cidr_blocks = ["0.0.0.0/0"]
    from_port      = 0
    to_port        = 65535
  }

  ingress {
    protocol       = "ANY"
    description    = "Входящий трафик от любых ресурсов внутри этой VPC"
    v4_cidr_blocks = [var.public_subnet_cidr, var.private_subnet_cidr]
    from_port      = 0
    to_port        = 65535
  }
}

resource "yandex_vpc_security_group" "database_sg" {
  name        = "${var.environment}-database-sg"
  description = "Группа безопасности базы данных для окружения ${var.environment}"
  network_id  = yandex_vpc_network.this.id

  labels = var.instance_tags

  egress {
    protocol       = "ANY"
    v4_cidr_blocks = [var.private_subnet_cidr]
    from_port      = 0
    to_port        = 65535
  }

  ingress {
    protocol          = "TCP"
    description       = "Доступ к PostgreSQL только для ресурсов из private-sg группы"
    port              = 5432
    security_group_id = yandex_vpc_security_group.private_sg.id
  }

  ingress {
    protocol          = "TCP"
    description       = "Доступ к Redis только для ресурсов из private-sg группы"
    port              = 6379
    security_group_id = yandex_vpc_security_group.private_sg.id
  }
}
