FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    npm install -g windmill-cli && \
    pip3 install --break-system-packages pytest-json-ctrf PyYAML requests && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /home/user/windmill-project

LABEL Author="generate-harbor-tasks"
LABEL Description="Windmill declarative-flow-retry task environment: Node.js v24, windmill-cli, and an empty /home/user/windmill-project workspace targeting https://app.windmill.dev."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - Node.js v24 (required by the windmill-cli, which needs Node >= 20)
#   - windmill-cli (`wmill`) installed globally via npm
#   - PyYAML for parsing flow.yaml in the verifier
#   - requests for any auxiliary HTTP verification
#   - /home/user/windmill-project: empty project directory the executor will populate
