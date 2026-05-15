FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV NODE_VERSION=20

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    gnupg \
    build-essential \
    git \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js v20 via NodeSource
RUN curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Verify Node.js and npm versions
RUN node --version && npm --version

# Install Windmill CLI globally
RUN npm install -g windmill-cli

# Verify wmill is available
RUN wmill --version

# Create user home and windmill project directory structure
RUN mkdir -p /home/user/windmill-project/f/workflows

# Set working directory
WORKDIR /home/user/windmill-project

# Install pytest for test runner
RUN pip3 install --break-system-packages pytest

# Note: /home/user/windmill-project/f/workflows/batch_enricher.ts
# is intentionally NOT created here — the agent must create it.
