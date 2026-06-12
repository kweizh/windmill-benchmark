FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    npm install -g windmill-cli && \
    pip3 install --break-system-packages pytest-json-ctrf requests && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

# Bootstrap the project skeleton expected by the task.
RUN mkdir -p /home/user/wac_accumulator/f && \
    cat >/home/user/wac_accumulator/wmill.yaml <<'EOF'
defaultTs: bun
includes:
  - f/**
excludes: []
codebases: []
skipVariables: false
skipResources: false
skipResourceTypes: true
skipSecrets: true
includeSchedules: false
includeTriggers: false
includeUsers: false
includeGroups: false
includeSettings: false
includeKey: false
EOF

LABEL Author="generate-harbor-tasks"
LABEL Description="Windmill task environment with windmill-cli on Node.js v24 for authoring and deploying a TypeScript WAC workflow that exercises per-flow user state."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - Node.js v24 for windmill-cli runtime
#   - windmill-cli installed globally via npm (provides the `wmill` binary)
#   - requests (used by final-state tests if needed for direct API checks)
#   - /home/user/wac_accumulator: bootstrapped Windmill project skeleton with wmill.yaml
#   - /home/user/wac_accumulator/f: folder root for declarative assets that the agent will populate
