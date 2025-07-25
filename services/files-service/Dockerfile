FROM python:3.13.2

COPY --from=ghcr.io/astral-sh/uv@sha256:2381d6aa60c326b71fd40023f921a0a3b8f91b14d5db6b90402e65a635053709 /uv /uvx /bin/

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

ADD . /app
WORKDIR /app

RUN uv sync --locked

CMD uv run alembic upgrade head; uv run src/main.py
