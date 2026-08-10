.PHONY: setup data train test lint all

setup:
	uv sync

data:
	uv run python scripts/download_data.py

train:
	uv run python scripts/train_model.py

test:
	uv run pytest -q

lint:
	uv run ruff check .

all: data train test lint
