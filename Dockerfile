FROM ghcr.io/astral-sh/uv:0.11.19-python3.12-trixie-slim
ARG TASK_VERSION=v3.53.1
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl tini \
    && rm -rf /var/lib/apt/lists/* \
    && sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b /usr/local/bin "$TASK_VERSION" \
    && useradd --uid 1000 --create-home app
WORKDIR /app
ENV UV_NO_DEV=1
COPY pyproject.toml uv.lock /app/
RUN uv sync --locked --no-install-project
COPY . /app
RUN uv sync --locked
USER app
ENV PYTHONUNBUFFERED=1 \
    UV_NO_SYNC=1 \
    UV_CACHE_DIR=/tmp/uv \
    TASK_TEMP_DIR=/tmp/task
EXPOSE 8000
# Task doesn't forward stop signals to the server; tini -g signals the whole process group.
ENTRYPOINT ["tini", "-g", "--"]
CMD ["task", "serve"]
