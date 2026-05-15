FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# ── System dependencies ────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        wget \
        ca-certificates \
        git \
        python3 \
        python3-pip \
        python3-pytest \
        bash \
    && rm -rf /var/lib/apt/lists/*

# ── Python wmill package ───────────────────────────────────────────────────────
RUN pip3 install --break-system-packages wmill

# ── Node.js v20 via NodeSource ─────────────────────────────────────────────────
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# ── Windmill CLI (wmill) from npm ──────────────────────────────────────────────
RUN npm install -g windmill-cli

# ── Project scaffold ───────────────────────────────────────────────────────────
RUN useradd -m -s /bin/bash user || true \
    && mkdir -p /home/user/windmill-project/f/workflows \
    && chown -R user:user /home/user

WORKDIR /home/user/windmill-project
