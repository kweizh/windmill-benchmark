FROM ubuntu:24.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    gnupg \
    python3 \
    python3-pip \
    python3-pytest \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js v20 via NodeSource
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Verify Node.js and npm versions
RUN node --version && npm --version

# Install windmill CLI globally via npm
RUN npm install -g windmill-client windmill-cli

# Verify wmill CLI is accessible
RUN wmill --version

# Create the user and windmill project directory structure
RUN mkdir -p /home/user/windmill-project/f/workflows

# Set working directory
WORKDIR /home/user/windmill-project

# Note: /home/user/windmill-project/f/workflows/deploy_with_rollback.ts
# is intentionally NOT created here — the agent must create it.
