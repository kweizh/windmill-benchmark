FROM ubuntu:24.04

# Install required system packages, Node.js v24 (the wmill CLI requires Node >= 20),
# the Bun runtime (Windmill TypeScript scripts run on Bun), the Windmill CLI,
# and Python dependencies used by the initial- and final-state tests.
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep unzip && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends nodejs && \
    npm install -g windmill-cli && \
    curl -fsSL https://bun.sh/install | bash && \
    ln -s /root/.bun/bin/bun /usr/local/bin/bun && \
    pip3 install --break-system-packages pytest-json-ctrf requests && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create the user home directory and the empty project workspace.
# The wmill workspace is registered and the cloud state is seeded at
# `test_initial_state.py` time, since those steps require runtime secrets.
RUN mkdir -p /home/user && chmod 0755 /home/user && \
    mkdir -p /home/user/project/f/eval && \
    printf 'defaultTs: bun\nincludes:\n  - f/**\nexcludes: []\ncodebases: []\n' \
        > /home/user/project/wmill.yaml && \
    printf 'summary: Evaluation folder\nowners: []\nextra_perms: {}\n' \
        > /home/user/project/f/eval/folder.meta.yaml

LABEL Author="generate-harbor-tasks"
LABEL Description="Windmill Cloud evaluation environment: wmill CLI, Bun runtime, and a pre-initialized local workspace at /home/user/project."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep unzip
#   - always required pip3 packages: pytest-json-ctrf
#   - extra pip3 packages: requests (used by tests for HTTP verification)
#   - Node.js v24 (required by the wmill CLI)
#   - windmill-cli installed globally via npm (the `wmill` command)
#   - Bun runtime symlinked to /usr/local/bin/bun
#   - /home/user/project: pre-initialized Windmill workspace folder
#     - /home/user/project/wmill.yaml: minimal sync config
#     - /home/user/project/f/eval/folder.meta.yaml: stub metadata for the `f/eval` folder
