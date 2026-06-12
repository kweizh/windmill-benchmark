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
RUN mkdir -p /home/user/promote-project && chmod 0755 /home/user/promote-project

LABEL Author="generate-harbor-tasks"
LABEL Description="Windmill CLI task environment for promoting a deployed script from a staging workspace to a production workspace on the cloud-hosted Windmill instance via wmill.yaml + wmill sync push."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - pyyaml for parsing wmill.yaml during verification
#   - Node.js v24 (required by windmill-cli, which requires Node >= 20)
#   - windmill-cli (`wmill`) installed globally via npm
#   - /home/user/promote-project: empty project directory the executor will initialise as a Windmill sync folder
