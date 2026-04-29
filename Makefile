.DEFAULT_GOAL := all

.PHONY: all
all: ## Show the available make targets.
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@fgrep "##" Makefile | fgrep -v fgrep

.PHONY: clean
clean: ## Clean the temporary files.
	rm -rf megalinter-reports
	rm -rf site

# TODO: Add more targets as needed.

# MkDocs

.PHONY: docs-install
docs-install: ## Install the dependencies for MkDocs.
	poetry install --only docs

.PHONY: docs-serve
docs-serve: docs-install ## Serve the documentation locally.
	poetry run mkdocs serve

.PHONY: docs-build
docs-build: docs-install ## Build the documentation.
	poetry run mkdocs build --site-dir site

.PHONY: docs-lint
docs-lint: ## Install and run the documentation linter (Markdownlint).
	npm install -g markdownlint-cli
	markdownlint .

.PHONY: docs-fix
docs-fix: ## Install and run the documentation linter with auto-fix (Markdownlint).
	npm install -g markdownlint-cli
	markdownlint . --fix

# Linting

# Primary Linting

# TODO: Add the primary linting target here.

# Megalinter

.PHONY: megalinter
megalinter: ## Run the Megalinter.
	docker run --platform linux/amd64 --rm \
    -v /var/run/docker.sock:/var/run/docker.sock:rw \
    -v $(shell pwd):/tmp/lint:rw \
    oxsecurity/megalinter:v8