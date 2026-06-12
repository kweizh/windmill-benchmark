FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    npm install -g windmill-cli && \
    pip3 install --break-system-packages pytest-json-ctrf requests wmill && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /home/user/wmtask && chmod 0755 /home/user/wmtask

LABEL Author="generate-harbor-tasks"
LABEL Description="Windmill cloud task environment with the wmill CLI for deploying a Python script that verifies HMAC-SHA256 webhook signatures."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - Node.js v24 (required by the Windmill CLI)
#   - windmill-cli (the `wmill` command) for authoring & deploying assets to https://app.windmill.dev
#   - Python `requests` for the final-state verifier to call the Windmill HTTP API
#   - Python `wmill` client (used by the Windmill Python script to read variables)
#   - /home/user/wmtask: empty working directory for the executor
