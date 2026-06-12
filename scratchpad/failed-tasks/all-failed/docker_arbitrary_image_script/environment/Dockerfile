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
RUN mkdir -p /home/user/myproject

LABEL Author="generate-harbor-tasks"
LABEL Description="Windmill cloud (https://app.windmill.dev) task environment with the wmill CLI for authoring and deploying a sandboxed Docker (alpine:3) script."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - Node.js v24 + windmill-cli (`wmill`) for authoring and deploying scripts to https://app.windmill.dev
#   - pip3 packages required by verifier: requests, PyYAML (parsing .script.yaml + calling Windmill REST API)
#   - /home/user/myproject: empty project directory; the executor authors and deploys the sandboxed
#     Docker script from this folder. No local Windmill instance is started — all interactions
#     target Windmill Cloud.
