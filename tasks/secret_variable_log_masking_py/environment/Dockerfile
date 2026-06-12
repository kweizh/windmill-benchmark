FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    npm install -g windmill-cli && \
    pip3 install --break-system-packages pytest-json-ctrf wmill requests pyyaml && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /home/user/myproject && chmod 0755 /home/user/myproject

LABEL Author="generate-harbor-tasks"
LABEL Description="Ubuntu 24.04 with Node.js 24, the Windmill CLI (windmill-cli), and the Python Windmill SDK (wmill) for the secret_variable_log_masking_py task."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - Node.js v24 (required to install the windmill-cli npm package)
#   - windmill-cli (the `wmill` CLI) installed globally via npm
#   - Python wmill SDK installed via pip3 for use inside the executor's Windmill Python script and the verifier
#   - requests and pyyaml installed via pip3 for use in tests/test_final_state.py
#   - /home/user/myproject: empty project directory where the executor bootstraps the Windmill workspace
