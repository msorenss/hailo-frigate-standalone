ENV_FILE ?= $(if $(wildcard .env),.env,.env.example)

.PHONY: check-host check-packages build up down logs ps

check-host:
	./scripts/check-host.sh

check-packages:
	./scripts/check-packages.sh

build: check-packages
	docker compose --env-file $(ENV_FILE) -f compose.yaml build

up:
	docker compose --env-file $(ENV_FILE) -f compose.yaml up -d

down:
	docker compose --env-file $(ENV_FILE) -f compose.yaml down

logs:
	docker compose --env-file $(ENV_FILE) -f compose.yaml logs -f --tail=200

ps:
	docker compose --env-file $(ENV_FILE) -f compose.yaml ps
