# Stage Builder
FROM python:3.13-alpine AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=off

RUN apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev \
    build-base

WORKDIR /usr/src/poetry

COPY ./uv.lock ./pyproject.toml ./
RUN pip install uv &&  \
    uv pip install --system --no-cache .

# Final Image
FROM python:3.13-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# ENV ALEMBIC_CONFIG=/usr/src/alembic/alembic.ini   # not used now

RUN apk add --no-cache \
    postgresql-client \
    libpq \
    netcat-openbsd \
    dos2unix \
    bash \
    curl

WORKDIR /usr/src/fastapi

COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin/ /usr/local/bin/
COPY ./src .
COPY ./commands /commands
# COPY ./alembic.ini /usr/src/alembic/alembic.ini   # commented out

RUN dos2unix /commands/*.sh && chmod +x /commands/*.sh
