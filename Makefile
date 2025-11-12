APP = restapi

test:
	@flake8 . --exclude .venv

compose:
	@command -v docker >/dev/null 2>&1 || { echo "docker not installed"; exit 1; }
	# Prefer the docker Compose plugin (v2+). Fallback to legacy docker-compose if plugin missing.
	@if docker compose version >/dev/null 2>&1; then \
		echo "Using 'docker compose' (plugin)"; \
		docker compose build; \
		docker compose up; \
	else \
		echo "'docker compose' plugin not found, falling back to legacy 'docker-compose'"; \
		docker-compose build; \
		docker-compose up; \
	fi
