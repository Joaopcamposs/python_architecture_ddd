# these will speed up builds, for docker-compose >= 1.25
export COMPOSE_DOCKER_CLI_BUILD=1
export DOCKER_BUILDKIT=1

all: down build up test

build:
	docker-compose build

up:
	docker-compose up -d

build-up:
	docker-compose up --build -d

down:
	docker-compose down --remove-orphans

test: up
	docker-compose run --rm --no-deps --entrypoint=pytest fastapi /tests/unit /tests/integration /tests/e2e

unit-tests:
	docker-compose run --rm --no-deps --entrypoint=pytest fastapi /tests/unit

integration-tests: up
	docker-compose run --rm --no-deps --entrypoint=pytest fastapi /tests/integration

e2e-tests: up
	docker-compose run --rm --no-deps --entrypoint=pytest fastapi /tests/e2e

logs:
	docker-compose logs --tail=25 fastapi

format:
	ruff format .