FROM python:3.12.2-slim-bookworm AS python-build-stage
ARG BUILD_ENVIRONMENT=local

# Install build deps
RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

WORKDIR /app

# Copy deps first (better cache)
COPY pyproject.toml uv.lock ./

# Install deps system-wide
RUN uv pip install --system --no-cache .

# Copy source
COPY . .


# =====================
# Runtime image
# =====================
FROM python:3.12.2-slim-bookworm AS python-run-stage
ARG BUILD_ENVIRONMENT=local
ARG APP_HOME=/app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    BUILD_ENV=${BUILD_ENVIRONMENT}

WORKDIR ${APP_HOME}

# Runtime deps
RUN apt-get update && apt-get install --no-install-recommends -y \
    sudo git bash-completion nano ssh \
    libpq-dev gettext \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

# Add non-root user
RUN addgroup --system django && \
    adduser --system --ingroup django django && \
    mkdir -p ${APP_HOME}/staticfiles ${APP_HOME}/logs && \
    chown django:django ${APP_HOME}/staticfiles ${APP_HOME}/logs && \
    chmod 775 ${APP_HOME}/staticfiles ${APP_HOME}/logs

# Copy installed deps + app from build stage
COPY --from=python-build-stage /usr/local /usr/local
COPY --from=python-build-stage /app /app

# Entrypoint scripts
COPY --chown=django:django ./docker/local/django/entrypoint.sh /entrypoint.sh
COPY --chown=django:django ./docker/local/django/start.sh /start.sh

RUN sed -i 's/\r$//g' /entrypoint.sh /start.sh && \
    chmod +x /entrypoint.sh /start.sh

USER django
ENTRYPOINT [ "/entrypoint.sh" ]
