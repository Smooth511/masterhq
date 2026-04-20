# Claude-MKII Docker Image
#
# Provides a containerised environment for the MCP server and CLI tool.
# The project directory is expected to be mounted at /project at runtime.
#
# Build:  docker build -t claude-mkii .
# Run:    docker-compose up

FROM python:3.11-slim

# ── System dependencies ───────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        curl \
    && rm -rf /var/lib/apt/lists/*

# ── Working directory ─────────────────────────────────────────────────────
WORKDIR /project

# ── Python dependencies ───────────────────────────────────────────────────
# Copy only the requirements files first so that the layer is cached unless
# dependencies change.
COPY mcp-server/requirements.txt /tmp/mcp-requirements.txt
COPY cli/requirements.txt /tmp/cli-requirements.txt
COPY tools/requirements.txt /tmp/tools-requirements.txt

RUN pip install --no-cache-dir \
        -r /tmp/mcp-requirements.txt \
        -r /tmp/cli-requirements.txt \
        -r /tmp/tools-requirements.txt

# ── Copy application code ─────────────────────────────────────────────────
# The full project directory is typically mounted at runtime via a volume,
# but we also copy it here so the image works standalone.
COPY mcp-server/ /project/mcp-server/
COPY cli/        /project/cli/
COPY tools/      /project/tools/

# ── Non-root user ─────────────────────────────────────────────────────────
RUN useradd -m -u 1000 appuser
USER appuser

# ── Environment ───────────────────────────────────────────────────────────
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# ── Default command: start the MCP server ────────────────────────────────
CMD ["python", "/project/mcp-server/server.py"]
