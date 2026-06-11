FROM ubuntu:24.04

# Install required apt packages, Node.js v24 (required for the Windmill CLI),
# Bun (target Windmill runtime), Windmill CLI, and required Python packages
# used by the initial- and final-state tests.
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep unzip && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    npm install -g windmill-cli && \
    curl -fsSL https://bun.sh/install | bash && \
    ln -s /root/.bun/bin/bun /usr/local/bin/bun && \
    pip3 install --break-system-packages pytest-json-ctrf && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Standard user-space directory required by the Harbor benchmark.
RUN mkdir -p /home/user && chmod 0755 /home/user

# Project skeleton expected by the task. The wmill.yaml configures Bun as the
# default TypeScript runtime and only syncs the f/** tree.
RUN mkdir -p /home/user/myproject/f/eval && \
    cat > /home/user/myproject/wmill.yaml <<'EOF'
defaultTs: bun
includes: ["f/**"]
excludes: []
codebases: []
EOF

LABEL Author="generate-harbor-tasks"
LABEL Description="Windmill cloud benchmark: Bun TypeScript script that queries a Postgresql resource and returns a row count."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep unzip
#   - always required pip3 packages: pytest-json-ctrf
#   - Node.js v24 for the Windmill CLI
#   - windmill-cli (provides the `wmill` binary) installed globally via npm
#   - Bun installed via the official installer, symlinked into /usr/local/bin
#   - /home/user/myproject: pre-created Windmill workspace folder with wmill.yaml
#   - /home/user/myproject/f/eval: pre-created directory for the script the agent must author
