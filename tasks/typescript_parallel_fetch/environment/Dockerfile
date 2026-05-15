FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    npm install -g windmill-cli && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Windmill WAC task environment with Node.js v20 and wmill CLI; windmill-project scaffold pre-created."

RUN mkdir -p /home/user/windmill-project/f/workflows

# Container contents:
#   - ubuntu:24.04 base image
#   - curl, wget, ca-certificates, git, python3, python3-pip, python3-pytest, bash
#   - Node.js v20 (via nodesource setup script)
#   - wmill CLI installed globally via npm
#   - /home/user/windmill-project/f/workflows  — pre-created scaffold directory

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
