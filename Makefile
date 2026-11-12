# Trivi'Hackathon 2026: the commands of the participants, the same on macOS, Linux and Windows (WSL, Git Bash,
# PowerShell). They run docker compose; Odoo installs and updates the modules by itself at start (docker/start.sh).

# Windows, make started from PowerShell or cmd (not from Git Bash, nor WSL): make would run the commands below
# with cmd.exe, but they need the POSIX shell and tools of Git for Windows. Detected as only cmd.exe expands %OS%.
ifneq ($(findstring Windows_NT,$(shell echo %OS%)),)
GIT_EXEC_PATH := $(strip $(shell git --exec-path))
ifeq ($(GIT_EXEC_PATH),)
$(error Git for Windows is not found: install it (PRE-REQUISITES.md), or run make from Git Bash or WSL)
endif
# e.g. C:/Program Files/Git/mingw64/libexec/git-core: Git is installed 3 folders above
GIT_ROOT := $(strip $(shell cd /d "$(subst /,\,$(GIT_EXEC_PATH))\..\..\.." && cd))
export PATH := $(GIT_ROOT)\usr\bin;$(PATH)
SHELL := sh.exe
endif

DB := trivia
# Docker must answer first: what to do, instead of "failed to connect to the docker API"
CHECK := @sh docker/check.sh --quiet
# install or update every trivia_* module in a one-off container (docker/start.sh), then stop: run while the
# server is stopped (two Odoo processes initialising the same database at the same time collide).
# No path on the command line: Git Bash (Windows) would turn /mnt/... into C:/Program Files/Git/mnt/...
ODOO_UPDATE := docker compose run --rm -e TRIVIA_STOP_AFTER_INIT=1
# start in the background, and wait until Odoo answers (healthcheck of docker-compose.yml): when the installation
# of the modules fails, Odoo stops, and the end of its logs shows why
UP := docker compose up -d --wait || { echo "--- the last logs of Odoo:"; docker compose logs --tail 30 odoo; \
	echo "Odoo did not start: see the error above (all the logs: make logs)."; exit 1; }

.PHONY: help check up debug down init update shell psql logs reset

help: ## Show this help
	@grep -E '^[a-z]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  make %-11s %s\n", $$1, $$2}'

check: ## Check that Docker is ready, and say what to do when it is not
	@sh docker/check.sh

up: ## Start Odoo and PostgreSQL in the background, wait until Odoo answers
	$(CHECK)
	@$(UP)

# attached to the container, its terminal is yours: a breakpoint stops Odoo and waits for your commands here.
# --sig-proxy=false: Ctrl+C leaves the session but does not stop Odoo
debug: ## Start Odoo, then attach to it to use ipdb / pudb breakpoints
	$(CHECK)
	@$(UP)
	@printf '%s\n' "Odoo runs with ipdb and pudb. Breakpoint: import pudb; pudb.set_trace()  (or ipdb)" \
		"Ctrl+C leaves the debugger session, Odoo keeps running."
	@docker compose attach --sig-proxy=false odoo

down: ## Stop the containers (the database is kept)
	$(CHECK)
	docker compose down

init: ## Create the database, with the trivia_* modules if any (first time)
	$(CHECK)
	docker compose stop odoo
	$(ODOO_UPDATE) odoo
	@$(UP)

# all the modules: nobody updates the wrong one
update: ## Update all the trivia_* modules and restart Odoo
	$(CHECK)
	docker compose stop odoo
	$(ODOO_UPDATE) -e TRIVIA_UPDATE=force odoo
	@$(UP)

shell: ## Open an Odoo shell on the database
	$(CHECK)
	docker compose exec odoo odoo shell -d $(DB)

psql: ## Open a PostgreSQL console on the database
	$(CHECK)
	docker compose exec db psql -U odoo $(DB)

logs: ## Follow the logs of Odoo
	$(CHECK)
	docker compose logs -f odoo

reset: ## Delete the containers AND the local database, to start over
	$(CHECK)
	docker compose down -v
