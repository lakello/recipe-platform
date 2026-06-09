# Ansible

Ansible-код для настройки Linux-серверов Recipe Platform.

Ansible используется после Terraform и отвечает за конфигурацию операционной системы внутри виртуальных машин: установку пакетов, настройку пользователей, SSH, firewall, Docker, hardening, fail2ban, node exporter и GitHub Actions self-hosted runner.

## Назначение директории

В директории `infra/ansible/` находится код configuration management:

- inventories для окружений;
- playbooks;
- roles;
- group variables;
- host variables;
- шаблоны конфигураций;
- Ansible Vault файлы, если будет использоваться;
- документация по запуску.

## Что Ansible делает в проекте

Ansible настраивает Linux VM, созданные через Terraform.

Основные задачи:

- обновление системных пакетов;
- создание пользователей;
- настройка SSH;
- настройка sudo;
- установка базовых утилит;
- установка Docker;
- настройка firewall;
- настройка fail2ban;
- Linux hardening;
- установка GitHub Actions self-hosted runner;
- установка node exporter;
- настройка системных сервисов;
- проверка состояния VM.

## Что Ansible не делает

Ansible не должен дублировать Terraform.

Ansible не отвечает за:

- создание VPC;
- создание subnet;
- создание security groups;
- создание Kubernetes cluster;
- создание Managed PostgreSQL;
- создание Managed Redis;
- создание Object Storage buckets;
- создание DNS-записей;
- создание VM как cloud-ресурса.

Эти задачи выполняются через Terraform.

Ansible также не должен деплоить основное приложение в Kubernetes, если для этого используется Helm/GitHub Actions.

## Разделение ответственности

| Задача                        | Инструмент                       |
| ----------------------------- | -------------------------------- |
| Создание cloud-инфраструктуры | Terraform                        |
| Настройка Linux внутри VM     | Ansible                          |
| Сборка Docker images          | GitHub Actions                   |
| Хранение images               | GitHub Container Registry        |
| Деплой приложения             | Helm                             |
| Запуск приложения             | Kubernetes                       |
| Observability приложения      | Prometheus, Grafana, Loki, Tempo |

## Целевые серверы

Ansible может настраивать следующие VM:

### Bastion host

Используется для безопасного административного доступа во внутреннюю сеть.

Настройки:

- SSH-доступ только по ключам;
- ограничение доступа по IP;
- fail2ban;
- firewall;
- системные обновления;
- audit tools;
- node exporter.

### Self-hosted GitHub Actions runner

Используется для выполнения CI/CD задач, если нужен runner внутри инфраструктуры.

Настройки:

- отдельный пользователь;
- GitHub Actions runner service;
- Docker;
- доступ к Kubernetes, если требуется;
- минимально необходимые права;
- monitoring agent / node exporter.

### Utility VM

Опциональная VM для вспомогательных задач:

- диагностика сети;
- backup scripts;
- kubectl/admin utilities;
- maintenance tasks.

## Рекомендуемая структура

```text

infra/ansible/

inventories/

dev/

hosts.yml

group_vars/

all.yml

host_vars/

prod/

hosts.yml

group_vars/

all.yml

host_vars/

playbooks/

site.yml

bastion.yml

github-runner.yml

hardening.yml

node-exporter.yml

roles/

common/

tasks/

handlers/

templates/

defaults/

vars/

meta/

users/

tasks/

defaults/

ssh/

tasks/

templates/

defaults/

firewall/

tasks/

templates/

defaults/

docker/

tasks/

handlers/

defaults/

fail2ban/

tasks/

templates/

defaults/

hardening/

tasks/

templates/

defaults/

github-runner/

tasks/

templates/

defaults/

node-exporter/

tasks/

templates/

defaults/

ansible.cfg

requirements.yml

README.md
```

## Inventories

Inventories описывают целевые серверы для окружений.

Пример `inventories/dev/hosts.yml`:

``` yaml
## all:

## children:

## bastion:

## hosts:

## recipe-platform-dev-bastion:

ansible_host: 203.0.113.10

ansible_user: ubuntu



## github_runners:

## hosts:

## recipe-platform-dev-runner:

ansible_host: 203.0.113.11

ansible_user: ubuntu
```

Пример `inventories/prod/hosts.yml`:

``` yaml
## all:

## children:

## bastion:

## hosts:

## recipe-platform-prod-bastion:

ansible_host: 203.0.113.20

ansible_user: ubuntu
```

## Group variables

Пример `group_vars/all.yml`:

``` yaml
project_name: recipe-platform

timezone: Europe/Moscow



## admin_users:

- name: deploy

## ssh_keys:

- "ssh-ed25519 AAAA..."



ssh_port: 22

disable_password_auth: true

disable_root_login: true



## firewall_allowed_tcp_ports:

- 22



install_node_exporter: true
```

## Секреты

Секреты нельзя хранить в открытом виде в Git.

Возможные подходы:

- Ansible Vault;
- GitHub Actions Secrets;
- Yandex Lockbox;
- переменные окружения CI;
- ручной ввод через `--ask-vault-pass`.

Примеры секретов:

- GitHub runner registration token;
- private SSH keys;
- credentials для monitoring;
- sensitive env vars.

Файлы с секретами должны быть исключены из Git.

Пример `.gitignore`:

```
*.vault.yml
.vault-password
private_key*
id_rsa*
id_ed25519*
```

## Ansible Vault

Если используется Ansible Vault:

Создать зашифрованный файл:

```
ansible-vault create inventories/prod/group_vars/vault.yml
```

Редактировать:

```
ansible-vault edit inventories/prod/group_vars/vault.yml
```

Запуск playbook с запросом пароля:

```
ansible-playbook -i inventories/prod/hosts.yml playbooks/site.yml --ask-vault-pass
```

## Playbooks

### `site.yml`

Главный playbook для полной настройки VM.

Примерный состав:

``` yaml
- name: Configure all servers

hosts: all

become: true

## roles:

- common

- users

- ssh

- firewall

- fail2ban

- hardening

- node-exporter
```

### `bastion.yml`

Настройка bastion host:

``` yaml
- name: Configure bastion host

hosts: bastion

become: true

## roles:

- common

- users

- ssh

- firewall

- fail2ban

- hardening

- node-exporter
```

### `github-runner.yml`

Настройка self-hosted GitHub Actions runner:

``` yaml
- name: Configure GitHub Actions runner

hosts: github_runners

become: true

## roles:

- common

- users

- docker

- github-runner

- node-exporter
```

## Roles

### `common`

Базовая настройка системы:

- update package cache;
- upgrade packages;
- установка базовых утилит;
- настройка timezone;
- настройка hostname;
- базовая диагностика.

Пакеты:

- curl;
- wget;
- git;
- vim;
- htop;
- unzip;
- jq;
- ca-certificates;
- gnupg;
- lsb-release.

### `users`

Управление пользователями:

- создание admin/deploy пользователей;
- добавление SSH keys;
- настройка sudo;
- отключение ненужных пользователей.

### `ssh`

Hardening SSH:

- отключение password authentication;
- отключение root login;
- настройка allowed users;
- настройка SSH port при необходимости;
- безопасные SSH options.

### `firewall`

Настройка firewall:

- разрешение SSH;
- разрешение node exporter только из monitoring network;
- запрет лишних входящих соединений;
- default deny incoming;
- allow outgoing.

В зависимости от ОС можно использовать:

- ufw;
- nftables;
- iptables.

### `docker`

Установка и настройка Docker:

- Docker Engine;
- Docker Compose plugin;
- добавление пользователя в docker group;
- настройка daemon.json;
- log rotation;
- автозапуск сервиса.

Docker нужен в основном для:

- self-hosted runner;
- вспомогательных задач;
- диагностики;
- локальных maintenance-контейнеров.

### `fail2ban`

Защита SSH от brute force:

- установка fail2ban;
- настройка jail для sshd;
- настройка ban time;
- настройка retry limits.

### `hardening`

Linux hardening:

- базовые sysctl-настройки;
- отключение ненужных сервисов;
- настройка audit/logging;
- ограничения прав;
- unattended upgrades, если применимо;
- проверка permissions.

### `github-runner`

Установка self-hosted GitHub Actions runner:

- создание пользователя runner;
- скачивание runner package;
- регистрация runner;
- установка systemd service;
- запуск сервиса;
- настройка labels.

Примеры labels:

```
self-hosted
linux
yandex-cloud
recipe-platform
dev
```

### `node-exporter`

Установка node exporter:

- скачивание binary;
- создание systemd service;
- запуск сервиса;
- настройка порта;
- ограничение доступа через firewall/security group.

Node exporter нужен для сбора метрик VM в Prometheus.

## Запуск Ansible

Проверить доступность хостов:

```
ansible -i inventories/dev/hosts.yml all -m ping
```

Запустить полный playbook для dev:

```
ansible-playbook -i inventories/dev/hosts.yml playbooks/site.yml
```

Запустить bastion playbook:

```
ansible-playbook -i inventories/dev/hosts.yml playbooks/bastion.yml
```

Запустить runner playbook:

```
ansible-playbook -i inventories/dev/hosts.yml playbooks/github-runner.yml
```

Для production:

```
ansible-playbook -i inventories/prod/hosts.yml playbooks/site.yml
```

## Dry run

Проверить изменения без применения:

```
ansible-playbook -i inventories/dev/hosts.yml playbooks/site.yml --check
```

Посмотреть diff:

```
ansible-playbook -i inventories/dev/hosts.yml playbooks/site.yml --check --diff
```

## Ограничение по хостам

Запустить только для одного хоста:

```
ansible-playbook -i inventories/dev/hosts.yml playbooks/site.yml --limit recipe-platform-dev-bastion
```

Запустить только конкретные теги:

```
ansible-playbook -i inventories/dev/hosts.yml playbooks/site.yml --tags docker
```

Пропустить теги:

```
ansible-playbook -i inventories/dev/hosts.yml playbooks/site.yml --skip-tags hardening
```

## Ansible configuration

Пример `ansible.cfg`:

``` ini
[defaults]

inventory = inventories/dev/hosts.yml

roles_path = roles

host_key_checking = True

retry_files_enabled = False

stdout_callback = yaml

interpreter_python = auto_silent



[ssh_connection]

pipelining = True
```

## Requirements

Если используются внешние роли или коллекции, они описываются в `requirements.yml`.

Установка:

``` bash
ansible-galaxy install -r requirements.yml

ansible-galaxy collection install -r requirements.yml
```

Пример:

``` yaml
## collections:

- name: community.docker

- name: ansible.posix
```

## Проверка качества

Рекомендуемые инструменты:

- ansible-lint;
- yamllint;
- molecule, если будет добавлено тестирование ролей.

Запуск:

``` bash
ansible-lint .

yamllint .
```

## CI/CD для Ansible

В GitHub Actions на Pull Request должны выполняться:

- YAML lint;
- ansible-lint;
- syntax check.

Пример syntax check:

```
ansible-playbook -i inventories/dev/hosts.yml playbooks/site.yml --syntax-check
```

Применение playbook к production должно быть только вручную и после approval.

## Безопасность

Основные требования:

- SSH только по ключам;
- root login отключён;
- password authentication отключена;
- firewall включён;
- fail2ban включён;
- пользователи имеют минимальные права;
- runner не должен иметь лишних privileges;
- secrets не хранятся в Git;
- production inventory защищён;
- доступ к bastion ограничен trusted IP;
- системные пакеты регулярно обновляются;
- Docker socket доступен только нужным пользователям.

## Monitoring

Ansible может устанавливать node exporter.

Prometheus будет собирать метрики:

- CPU;
- RAM;
- disk usage;
- filesystem;
- network;
- system load;
- systemd services.

Важно:

- не открывать node exporter в Internet;
- ограничить доступ security group или firewall;
- использовать internal network, если возможно.

## Idempotency

Playbooks и roles должны быть идемпотентными.

Это значит:

- повторный запуск не должен ломать сервер;
- повторный запуск не должен постоянно менять состояние без причины;
- handlers должны вызываться только при изменениях;
- tasks должны использовать Ansible-модули, а не shell, где возможно.

## Порядок работы после Terraform

1. 1.Terraform создаёт VM.
2. 2.Terraform output отдаёт public IP или private IP.
3. 3.IP добавляется в Ansible inventory.
4. 4.Ansible проверяет доступность по SSH.
5. 5.Ansible запускает common/base настройку.
6. 6.Ansible применяет роли по назначению сервера.
7. 7.Monitoring начинает собирать метрики.

## Troubleshooting

Проверка SSH:

```
ssh ubuntu@<server-ip>
```

Проверка Ansible ping:

```
ansible -i inventories/dev/hosts.yml all -m ping -vvv
```

Проверка фактов:

```
ansible -i inventories/dev/hosts.yml all -m setup
```

Запуск с подробным выводом:

```
ansible-playbook -i inventories/dev/hosts.yml playbooks/site.yml -vvv
```

## Статус

Не начато. Запланировано на следующий (DevOps) этап.

После второго этапа разработки директория `infra/ansible/` содержит только этот README.

Приоритет реализации:

1. Базовая структура inventories/playbooks/roles.
2. Role `common`.
3. Role `users`.
4. Role `ssh`.
5. Role `firewall`.
6. Role `docker`.
7. Role `fail2ban`.
8. Role `hardening`.
9. Role `github-runner`.
10. Role `node-exporter`.
11. ansible-lint в CI.
