FROM ubuntu:24.04

# ── system dependencies ────────────────────────────────────────────────────────
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    git \
    gnupg \
    python3 \
    python3-pip \
    python3-pytest \
    unzip \
    wget \
    && rm -rf /var/lib/apt/lists/*

# ── Node.js v20 (via NodeSource) ───────────────────────────────────────────────
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# ── Windmill CLI (windmill-client npm package exposes `wmill`) ─────────────────
RUN npm install -g windmill-cli

# ── Project scaffolding ────────────────────────────────────────────────────────
# Create the project directory tree (the agent must create etl_orchestrator.ts)
RUN mkdir -p /home/user/windmill-project/f/workflows

# Initialise the deduplication state file with an empty array
RUN echo '[]' > /home/user/windmill-project/processed_events.json

# Verify the CLI is reachable
RUN wmill --version

# ── Default working directory ──────────────────────────────────────────────────
WORKDIR /home/user/windmill-project
