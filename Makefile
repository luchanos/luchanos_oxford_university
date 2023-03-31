up:
	docker compose -f docker-compose-local.yaml up -d

down:
	docker compose -f docker-compose-local.yaml down && docker network prune --force

run:
	docker compose -f docker-compose-ci.yaml up -d
