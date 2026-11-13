# syntax=docker/dockerfile:1

FROM python:3.12-slim-trixie AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# --- dépendances et paquet installés dans /app/.venv ---
FROM base AS builder
COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/app/.venv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-install-project
COPY README.md ./
COPY src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-editable

# --- lint + tests (bin/test) ---
FROM builder AS test
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable
COPY tests ./tests
COPY sources.csv ./
ENV PATH=/app/.venv/bin:$PATH
CMD ["sh", "-c", "ruff check . && ruff format --check . && pytest"]

# --- image finale : venv seul, utilisateur non root ---
FROM base AS runtime
RUN useradd --uid 1000 --create-home gazette
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY sources.csv ./
RUN mkdir -p /app/data && chown gazette:gazette /app/data
ENV PATH=/app/.venv/bin:$PATH \
    SOURCES_PATH=/app/sources.csv \
    DATA_DIR=/app/data
USER gazette
CMD ["gazette", "serve"]
