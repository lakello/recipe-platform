resource "yandex_vpc_address" "bastion_ip" {
  name = "bastion-static-ip"
  external_ipv4_address {
    zone_id = var.zone
  }
}

resource "yandex_vpc_security_group" "bastion_sg" {
  name       = "bastion-security-group"
  network_id = var.network_id

  ingress {
    protocol       = "TCP"
    description    = "Доступ по SSH из разрешенного IP"
    v4_cidr_blocks = [var.allowed_ssh_cidr]
    port           = 22
  }

  egress {
    protocol       = "ANY"
    description    = "Разрешить весь исходящий трафик"
    v4_cidr_blocks = ["0.0.0.0/0"]
    from_port      = 0
    to_port        = 65535
  }
}

resource "yandex_compute_instance" "bastion" {
  name        = "bastion_host"
  platform_id = "standard-v3"
  zone        = var.zone

  resources {
    cores  = 2
    memory = 2
  }

  boot_disk {
    initialize_params {
      image_id = var.image_id
      size     = 20
      type     = "network-ssd"
    }
  }

  network_interface {
    subnet_id          = var.subnet_id
    nat                = true
    nat_ip_address     = yandex_vpc_address.bastion_ip.external_ipv4_address[0].address
    security_group_ids = [yandex_vpc_security_group.bastion_sg.id]
  }

  metadata = {
    ssh-keys = "${var.ssh_user}:${var.ssh_public_key}"
  }
}
