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

# Copy only dependency files first for better layer caching
COPY pyproject.toml uv.lock ./

# Create virtual environment and install dependencies
# This layer will be cached unless pyproject.toml or uv.lock changes
RUN uv venv /opt/venv && \
    . /opt/venv/bin/activate && \
    uv pip install --no-cache-dir --compile-bytecode --link-mode=copy .

# Copy source code (this will invalidate cache only when source changes)
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

# Add non-root user (match host UID/GID)
ARG UID=1000
ARG GID=1000

RUN addgroup --gid ${GID} django && \
    adduser --uid ${UID} --gid ${GID} --disabled-password django && \
    mkdir -p ${APP_HOME}/staticfiles ${APP_HOME}/logs && \
    chown -R django:django ${APP_HOME}


# Copy virtual environment and app from build stage
COPY --from=python-build-stage /opt/venv /opt/venv
COPY --from=python-build-stage /app /app

# Ensure proper permissions after copying
RUN chown -R django:django ${APP_HOME}

# Activate virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Entrypoint scripts
COPY --chown=django:django ./docker/local/django/entrypoint.sh /entrypoint.sh
COPY --chown=django:django ./docker/local/django/start.sh /start.sh
COPY --chown=django:django ./docker/local/django/celery/worker/start.sh /start-celeryworker.sh
COPY --chown=django:django ./docker/local/django/celery/beat/start.sh /start-celerybeat.sh
COPY --chown=django:django ./docker/local/django/celery/flower/start.sh /start-flower.sh

RUN sed -i 's/\r$//g' /entrypoint.sh /start.sh  \
    /start-celerybeat.sh \
    /start-flower.sh \
    /start-celeryworker.sh && \
    chmod +x /entrypoint.sh /start.sh  /start-celerybeat.sh /start-flower.sh /start-celeryworker.sh 

USER django
ENTRYPOINT [ "/entrypoint.sh" ]
