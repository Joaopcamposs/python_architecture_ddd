# these will speed up builds, for docker-compose >= 1.25
export COMPOSE_DOCKER_CLI_BUILD=1
export DOCKER_BUILDKIT=1

local-enviroment:
	python -m venv venv_eda && venv_eda\Scripts\Activate.ps1

install-dependencies:
	python.exe -m pip install --upgrade pip && pip install -r requirements.txt

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
	docker-compose logs --tail=300 fastapi redis_pubsub

postgres:
	docker-compose up -d postgres

format:
	ruff format .

create_initial_tables:
	docker-compose exec -i postgres psql -U allocation -d allocation -c\
        "CREATE TABLE IF NOT EXISTS order_lines ( \
            id SERIAL PRIMARY KEY, \
            sku VARCHAR(255), \
            qty INTEGER NOT NULL, \
            orderid VARCHAR(255) \
        ); \
        CREATE TABLE IF NOT EXISTS products ( \
            sku VARCHAR(255) PRIMARY KEY, \
            version_number INTEGER NOT NULL DEFAULT 0 \
        ); \
		CREATE TABLE IF NOT EXISTS batches ( \
            id SERIAL PRIMARY KEY, \
            reference VARCHAR(255), \
            sku VARCHAR(255) REFERENCES products(sku), \
            purchased_quantity INTEGER NOT NULL, \
            eta DATE \
        ); \
        CREATE TABLE IF NOT EXISTS allocations ( \
			id SERIAL PRIMARY KEY, \
			orderline_id INTEGER REFERENCES order_lines(id), \
			batch_id INTEGER REFERENCES batches(id) \
		); \
		CREATE TABLE IF NOT EXISTS allocations_view ( \
			orderid VARCHAR(255), \
			sku VARCHAR(255), \
			batchref VARCHAR(255) \
		);"