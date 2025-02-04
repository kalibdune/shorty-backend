ifeq ($(shell test -e '.env' && echo -n yes),yes)
	include .env
endif

# Manually define main variables

ifndef APP_PORT
override APP_PORT = 8000
endif

ifndef APP_HOST
override APP_HOST = 127.0.0.1
endif

# parse additional args for commands

args := $(wordlist 2, 100, $(MAKECMDGOALS))
ifndef args
MESSAGE = "No such command (or you pass two or many targets to ). List of possible commands: make help"
else
MESSAGE = "Done"
endif

APPLICATION_NAME = shorty
APPLICATION_HOST = 127.0.0.1
APPLICATION_PORT = 8000
TEST = poetry run python -m pytest --log-level=debug --showlocals --verbose
CODE = $(APPLICATION_NAME) tests

HELP_FUN = \
	%help; while(<>){push@{$$help{$$2//'options'}},[$$1,$$3] \
	if/^([\w-_]+)\s*:.*\#\#(?:@(\w+))?\s(.*)$$/}; \
    print"$$_:\n", map"  $$_->[0]".(" "x(20-length($$_->[0])))."$$_->[1]\n",\
    @{$$help{$$_}},"\n" for keys %help; \

# Commands
dev_env:  ##@Environment Create .env file with variables
	@$(eval SHELL:=/bin/bash)
	@cp .env.example .env

docker_env:  ##@Environment Create .env file with variables
	@$(eval SHELL:=/bin/bash)
	@if [ -e .env.docker ]; then \
		cp .env.docker .env; \
	else \
		echo ".env.docker not found"; \
	fi

test_env:
	@$(eval SHELL:=/bin/bash)
	@if [ -e .env.test ]; then \
		cp .env.test .env; \
	else \
		echo ".env.test not found"; \
	fi

help: ##@Help Show this help
	@echo -e "Usage: make [target] ...\n"

migrate:  ##@Database Do all migrations in database
	make dev_env
	alembic upgrade $(args)

run:  ##@Application Run application server
	make dev_env
	poetry run python3 -m $(APPLICATION_NAME)

revision:  ##@Database Create new revision file automatically with prefix (ex. 2022_01_01_14cs34f_message.py)
	alembic revision --autogenerate

test:  ##@Testing Test application with pytest
	make test_env
	docker run --name test_postgres -e POSTGRES_USER=admin -e POSTGRES_PASSWORD=admin_password -e POSTGRES_DB=test -p 5433:5432 -d postgres:16
	$(TEST)
	docker stop test_postgres
	docker rm test_postgres

test-cov:  ##@Testing Test application with pytest and create coverage report
	make db && $(TEST) --cov=$(APPLICATION_NAME) --cov-report html --cov-fail-under=70

up:
	make docker_env
	docker-compose -f docker-compose.yml up -d --build

%::
	echo $(MESSAGE)

down:
	docker-compose -f docker-compose.yml down

stop:
	docker-compose -f docker-compose.yml stop

restart:
	make down
	make run

install:
	poetry shell
	poetry install
