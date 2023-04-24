export DOCKER_DEFAULT_PLATFORM=linux/amd64  # resolve problem for mac m1 chip

up:
	docker compose -f docker-compose-local.yaml up -d

down:
	docker compose -f docker-compose-local.yaml down --remove-orphans

up_ci:
	docker compose -f docker-compose-ci.yaml up -d

up_ci_rebuild:
	docker compose -f docker-compose-ci.yaml up --build -d

down_ci:
	docker compose -f docker-compose-local.yaml down --remove-orphans
