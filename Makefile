# Unix parity for scripts/*.ps1. Windows is the primary environment; make is not required.
PY := .venv/bin/python

.PHONY: dev test seed reset lint

dev:
	$(PY) -m uvicorn avise.api.app:app --reload --port 8000 --no-access-log

test:
	$(PY) -m pytest
	@if [ -f web/package.json ]; then cd web && npm run typecheck; fi

seed:
	$(PY) -m alembic upgrade head
	$(PY) -m tools.seed

reset:
	docker compose down -v
	docker compose up -d db
	$(PY) -m alembic upgrade head
	$(PY) -m tools.seed
	rm -rf uploads && mkdir -p uploads

lint:
	$(PY) -m ruff check avise tools tests
	$(PY) -m mypy avise
	@if [ -f web/package.json ]; then cd web && npm run typecheck; fi
