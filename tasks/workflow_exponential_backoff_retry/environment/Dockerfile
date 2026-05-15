FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    ca-certificates \
    git \
    python3 \
    python3-pip \
    python3-pytest \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js v20 via NodeSource
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Windmill CLI (installs as `wmill`)
RUN npm install -g windmill-cli

# Create user home directory
RUN mkdir -p /home/user

# Create the Windmill project directory structure (without api_caller.ts)
RUN mkdir -p /home/user/windmill-project/f/workflows

WORKDIR /home/user/windmill-project
