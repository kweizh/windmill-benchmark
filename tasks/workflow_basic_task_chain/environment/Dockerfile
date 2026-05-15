FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install the Windmill CLI (wmill)
RUN npm install -g windmill-cli

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Windmill WAC task environment with wmill CLI and Node.js v20, project scaffold at /home/user/windmill-project."

# Create the Windmill project scaffold
RUN mkdir -p /home/user/windmill-project && \
    cd /home/user/windmill-project && \
    cat >wmill.yaml <<'EOF'
defaultTs: bun
EOF

# Pre-install windmill-client so the agent can run/type-check locally
RUN cd /home/user/windmill-project && \
    npm init -y && \
    npm install windmill-client

# Container contents:
#   - curl, wget, ca-certificates, git, python3, python3-pip, python3-pytest, bash
#   - Node.js v20 (via nodesource)
#   - wmill CLI at /usr/local/bin/wmill
#   - /home/user/windmill-project  — Windmill project root with wmill.yaml
#   - windmill-client npm package installed in the project

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
