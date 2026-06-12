FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    npm install -g windmill-cli && \
    pip3 install --break-system-packages pytest-json-ctrf requests jsonschema && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /home/user/wm-agent && chmod 0755 /home/user/wm-agent

LABEL Author="generate-harbor-tasks"
LABEL Description="Windmill AI Agent task environment with windmill-cli and Node.js v24, targeting the cloud Windmill instance."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - Node.js v24 for Windmill CLI (windmill-cli requires Node >= 20)
#   - Windmill CLI (`wmill`) installed globally for deploying assets to the cloud Windmill workspace
#   - pip3 packages used by tests: requests, jsonschema
#   - /home/user/wm-agent: empty project directory the executor will populate
