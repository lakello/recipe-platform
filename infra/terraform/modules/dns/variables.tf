variable "zone_name" {
  description = "Имя DNS-зоны, обязательно с точкой на конце (например, 'example.com.')"
  type        = string
}

variable "ingress_ip" {
  description = "IP-адрес, на который будут указывать создаваемые A-записи"
  type        = string
}

variable "subdomains" {
  description = "Список поддоменов для создания A-записей (для корневого домена используйте пустую строку '')"
  type        = list(string)
  default     = ["", "dev", "staging", "api", "grafana"]
}

variable "create_wildcard" {
  description = "Флаг для создания wildcard-записи (*.example.com)"
  type        = bool
  default     = true
}

variable "ttl" {
  description = "Время кэширования DNS-записей (TTL) в секундах"
  type        = number
  default     = 300
}
