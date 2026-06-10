ENV ?= dev
BACKEND_CONFIG ?= backend.hcl
VAR_FILE ?= terraform.tfvars

YELLOW := \033[1;33m
GREEN  := \033[1;32m
NC     := \033[0m # No Color

.PHONY: all init plan apply destroy fmt validate clean

all: fmt validate plan

init:
	@echo "$(YELLOW)==> Инициализация Terraform для окружения [$(ENV)]...$(NC)"
	terraform init -backend-config=$(BACKEND_CONFIG)

fmt:
	@echo "$(YELLOW)==> Форматирование кода...$(NC)"
	terraform fmt -recursive

validate:
	@echo "$(YELLOW)==> Валидация конфигурации...$(NC)"
	terraform validate

plan: fmt validate
	@echo "$(YELLOW)==> Создание плана изменений для [$(ENV)]...$(NC)"
	terraform plan -var-file=$(VAR_FILE) -out=$(ENV).tfplan

apply:
	@echo "$(GREEN)==> Применение изменений для [$(ENV)]...$(NC)"
	@if [ -f $(ENV).tfplan ]; then \
		terraform apply $(ENV).tfplan && rm $(ENV).tfplan; \
	else \
		echo "$(YELLOW)Файл плана $(ENV).tfplan не найден. Запуск обычного apply...$(NC)"; \
		terraform apply -var-file=$(VAR_FILE); \
	fi

destroy:
	@echo "$(YELLOW)==> ВНИМАНИЕ: Удаление инфраструктуры [$(ENV)]...$(NC)"
	terraform destroy -var-file=$(VAR_FILE)

clean:
	@echo "$(YELLOW)==> Очистка локальных кэшей и планов...$(NC)"
	rm -f *.tfplan
	rm -rf .terraform/

help:
	@echo "Доступные команды:"
	@echo "  make init     - Инициализировать бэкенд ($(BACKEND_CONFIG))"
	@echo "  make plan     - Посмотреть изменения и сохранить в файл плана"
	@echo "  make apply    - Применить изменения"
	@echo "  make destroy  - Уничтожить инфраструктуру"
	@echo "  make clean    - Удалить локальный кэш и файлы .tfplan"
