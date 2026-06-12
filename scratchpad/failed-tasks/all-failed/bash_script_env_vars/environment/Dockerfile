FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep jq && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    npm install -g windmill-cli && \
    pip3 install --break-system-packages pytest-json-ctrf && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /home/user/myproject

LABEL Author="generate-harbor-tasks"
LABEL Description="Windmill task environment with the wmill CLI (windmill-cli npm package) pre-installed for deploying and running Bash scripts against the cloud-hosted Windmill workspace at app.windmill.dev."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - extra apt package jq for ad-hoc JSON inspection by the agent
#   - always required pip3 packages: pytest-json-ctrf
#   - Node.js v24 + windmill-cli (the `wmill` binary) for cloud workspace management
#   - /home/user/myproject: empty project directory ready for `wmill init` / `wmill sync pull`
