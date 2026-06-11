FROM ubuntu:24.04

# Core OS dependencies, Python toolchain, Node.js (for windmill-cli), and the
# cloudflared binary (used by the verifier to expose the local concurrency-
# tracking HTTP server to Windmill cloud workers).
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep \
        jq lsof procps && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    npm install -g windmill-cli && \
    curl -fsSL -o /usr/local/bin/cloudflared \
        https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 && \
    chmod +x /usr/local/bin/cloudflared && \
    pip3 install --break-system-packages pytest-json-ctrf requests && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# /home/user is the conventional task root for Harbor evaluation containers.
RUN mkdir -p /home/user && chmod 0755 /home/user

# Pre-initialise the Windmill workspace directory at /home/user/myproject with
# the minimal `wmill.yaml` and folder layout expected by the Windmill CLI.
# Workspace registration with `wmill workspace add` happens at evaluation time
# (in test_initial_state.py) because it needs the WINDMILL_TOKEN secret.
RUN mkdir -p /home/user/myproject/f/eval && \
    cat >/home/user/myproject/wmill.yaml <<'EOF'
defaultTs: bun
includes:
  - 'f/**'
excludes: []
codebases: []
skipScripts: false
skipFlows: false
skipApps: false
skipFolders: false
skipResources: false
skipResourceTypes: false
skipSecrets: false
skipVariables: false
skipSchedules: false
includeSchedules: true
includeUsers: false
includeGroups: false
includeSettings: false
includeKey: false
EOF

LABEL Author="generate-harbor-tasks"
LABEL Description="Windmill cloud (https://app.windmill.dev) WAC task environment with wmill CLI, cloudflared, and a pre-initialised /home/user/myproject workspace folder."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - extra apt packages: jq lsof procps (used by the verifier)
#   - always required pip3 packages: pytest-json-ctrf
#   - extra pip3 packages: requests (used by initial- and final-state tests)
#   - Node.js v24 + windmill-cli (`wmill` binary) for Workflows-as-Code authoring/deploy/run
#   - cloudflared binary at /usr/local/bin/cloudflared to expose the local HTTP server publicly
#   - /home/user/myproject: pre-initialised Windmill workspace folder with `wmill.yaml`
#   - /home/user/myproject/f/eval: pre-created folder so the agent can drop `fanout_workflow.ts`
