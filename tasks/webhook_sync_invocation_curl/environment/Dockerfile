FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep jq && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    npm install -g windmill-cli && \
    pip3 install --break-system-packages pytest-json-ctrf requests && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /home/user/windmill-webhook && chmod 0755 /home/user/windmill-webhook

LABEL Author="generate-harbor-tasks"
LABEL Description="Windmill CLI environment for deploying a script to the cloud and exercising its synchronous webhook with curl."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - additional apt packages: jq for JSON inspection during the task
#   - always required pip3 packages: pytest-json-ctrf
#   - additional pip3 packages: requests (used by tests/test_final_state.py to call the Windmill API)
#   - Node.js v24 plus windmill-cli (the `wmill` binary) for deploying scripts to https://app.windmill.dev
#   - /home/user/windmill-webhook: empty project directory where the executor will author the script and capture the HTTP response
