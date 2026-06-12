FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    npm install -g windmill-cli && \
    pip3 install --break-system-packages pytest-json-ctrf requests PyYAML && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /home/user/wmill-project && chmod 0755 /home/user/wmill-project

LABEL Author="generate-harbor-tasks"
LABEL Description="Windmill CLI (Node.js 24) for authoring, deploying, and running a declarative two-step flow against the cloud Windmill instance."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - Node.js v24 (for the windmill-cli npm package)
#   - windmill-cli installed globally via npm (provides the `wmill` binary)
#   - additional pip3 packages for verifier: requests, PyYAML
#   - /home/user/wmill-project: empty project directory where the agent will author the flow YAML
