
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

resource "yandex_vpc_security_group" "ingress_sg" {
  name        = "${var.environment}-ingress-sg"
  description = "HTTP/HTTPS из интернета и health checks"
  network_id  = yandex_vpc_network.this.id

  labels = var.instance_tags

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

resource "yandex_vpc_security_group" "postgresql_sg" {
  name        = "${var.environment}-postgresql-sg"
  description = "Группа безопасности postgresql для окружения ${var.environment}"
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
    description       = "Доступ к PostgreSQL"
    port              = 5432
    security_group_id = yandex_vpc_security_group.nodes_sg.id
  }
}

resource "yandex_vpc_security_group" "redis_sg" {
  name        = "${var.environment}-redis-sg"
  description = "Группа безопасности Redis для окружения ${var.environment}"
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
    description       = "Доступ к Redis"
    port              = 6379
    security_group_id = yandex_vpc_security_group.nodes_sg.id
  }
}

resource "yandex_vpc_security_group" "control_plane_sg" {
  name        = "${var.environment}-control_plane-sg"
  description = "Kubernetes API только от административной точки ${var.environment}"
  network_id  = yandex_vpc_network.this.id

  labels = var.instance_tags

  egress {
    protocol       = "ANY"
    description    = "Служебный трафик к worker nodes"
    v4_cidr_blocks = [var.private_subnet_cidr]
  }

  egress {
    protocol       = "TCP"
    description    = "Доступ к metric-server"
    port           = 4443
    v4_cidr_blocks = [var.cluster_ipv4_range]
  }

  egress {
    protocol       = "UDP"
    description    = "Синхронизация времени"
    port           = 123
    v4_cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    protocol       = "TCP"
    description    = "Доступ к Kubernetes API серверу"
    port           = 443
    v4_cidr_blocks = [var.admin_cidr]
  }

  ingress {
    protocol       = "TCP"
    description    = "Доступ к Kubernetes API серверу"
    port           = 6443
    v4_cidr_blocks = [var.admin_cidr]
  }
}

resource "yandex_vpc_security_group" "nodes_sg" {
  name        = "${var.environment}-nodes_sg"
  description = "Служебный трафик control plane, pod/service CIDR и health checks"
  network_id  = yandex_vpc_network.this.id

  labels = var.instance_tags

  egress {
    protocol       = "ANY"
    v4_cidr_blocks = ["0.0.0.0/0"]
    from_port      = 0
    to_port        = 65535
  }

  ingress {
    protocol          = "TCP"
    description       = "kubelet API для управления узлами"
    port              = 10250
    security_group_id = yandex_vpc_security_group.control_plane_sg.id
  }

  ingress {
    protocol       = "ICMP"
    description    = "для healthcheck от балансировщика"
    v4_cidr_blocks = [var.public_subnet_cidr, var.private_subnet_cidr]
  }

  ingress {
    protocol          = "ANY"
    description       = "для обмена данными между узлами кластера"
    predefined_target = "self_security_group"
  }
}
