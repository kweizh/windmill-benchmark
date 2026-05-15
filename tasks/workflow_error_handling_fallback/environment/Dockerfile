FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install wmill CLI (Windmill CLI)
RUN curl -fsSL https://raw.githubusercontent.com/windmill-labs/windmill/main/cli/install.sh | bash \
    || pip3 install wmill

# Install pytest for running test scripts
RUN pip3 install pytest

# Set up the windmill project directory structure
RUN mkdir -p /home/user/windmill-project/f/workflows

# Write the broken (initial) data_pipeline.ts — no try/catch around fetchData
COPY data_pipeline.ts /home/user/windmill-project/f/workflows/data_pipeline.ts

# Ensure the home user owns the project directory
RUN useradd -m -s /bin/bash user && chown -R user:user /home/user/windmill-project

WORKDIR /home/user/windmill-project
