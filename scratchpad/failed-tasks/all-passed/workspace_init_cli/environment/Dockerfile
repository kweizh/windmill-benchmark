FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    npm install -g windmill-cli && \
    pip3 install --break-system-packages pytest-json-ctrf pyyaml && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /home/user/myproject

LABEL Author="generate-harbor-tasks"
LABEL Description="Windmill cloud (https://app.windmill.dev) task environment with the wmill CLI preinstalled for bootstrapping a project folder via 'wmill init'."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - Node.js v24 + windmill-cli (`wmill`) for bootstrapping a Windmill project against https://app.windmill.dev
#   - pyyaml pip package for YAML-based verification of the generated wmill.yaml file
#   - /home/user/myproject: empty working directory where the agent runs `wmill init` to produce wmill.yaml
