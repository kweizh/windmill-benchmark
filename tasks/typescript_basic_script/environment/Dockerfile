FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-pytest bash && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    npm install -g windmill-cli && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Windmill TypeScript script task environment with Node.js v24 and wmill CLI installed."

RUN mkdir -p /home/user/windmill-project/f/scripts

# Container contents:
#   - curl, ca-certificates, git, python3, python3-pip, python3-pytest, bash — always-required base packages
#   - Node.js v24 (via nodesource setup_24.x)
#   - windmill-cli (wmill) installed globally via npm
#   - /home/user/windmill-project/f/scripts/ — empty scripts directory ready for the agent to populate

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
