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
LABEL Description="Windmill WAC task environment with wmill CLI and Node.js v20, project scaffold at /home/user/windmill-project. report_generator.ts is intentionally absent — agents must create it."

# Create the Windmill project scaffold with f/workflows/ directory,
# but do NOT create report_generator.ts (that is the agent's task).
RUN mkdir -p /home/user/windmill-project/f/workflows && \
    cd /home/user/windmill-project && \
    cat >wmill.yaml <<'EOF'
defaultTs: bun
EOF

# Pre-install windmill-client so the agent can use it locally
RUN cd /home/user/windmill-project && \
    npm init -y && \
    npm install windmill-client

# Container contents:
#   - curl, wget, ca-certificates, git, python3, python3-pip, python3-pytest, bash
#   - Node.js v20 (via nodesource)
#   - wmill CLI at /usr/local/bin/wmill
#   - /home/user/windmill-project  — Windmill project root with wmill.yaml
#   - /home/user/windmill-project/f/workflows/  — target directory (empty)
#   - windmill-client npm package installed in the project
#   - report_generator.ts is NOT present (agent must create it)

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
