FROM ubuntu:24.04

# Core OS dependencies, Python toolchain, Node.js (for the windmill-cli).
# The Windmill task uses the cloud instance at https://app.windmill.dev — no
# local Windmill server is started inside the container.
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep \
        jq && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    npm install -g windmill-cli && \
    pip3 install --break-system-packages pytest-json-ctrf requests PyYAML && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# /home/user is the conventional task root for Harbor evaluation containers.
RUN mkdir -p /home/user && chmod 0755 /home/user

# Pre-initialise the Windmill workspace directory at /home/user/myproject with
# a minimal `wmill.yaml` whose `excludes: []` starts empty. The agent must
# extend `excludes:` with a glob matching `f/gitops_<SAFE_ID>/legacy.ts` to
# protect the pre-seeded remote-only legacy script from destructive
# `wmill sync push --yes`. Workspace registration with `wmill workspace add`
# happens at evaluation time (in test_initial_state.py) because it needs the
# WINDMILL_TOKEN secret.
RUN mkdir -p /home/user/myproject && \
    cat >/home/user/myproject/wmill.yaml <<'EOF'
defaultTs: bun
includes:
  - 'f/**'
excludes: []
extraIncludes: []
codebases: []
skipVariables: true
skipResources: true
skipResourceTypes: true
skipSecrets: true
skipScripts: false
skipFlows: false
skipApps: false
skipFolders: false
includeSchedules: false
includeTriggers: false
includeUsers: false
includeGroups: false
includeSettings: false
includeKey: false
EOF

LABEL Author="generate-harbor-tasks"
LABEL Description="Windmill cloud (https://app.windmill.dev) GitOps task environment with the wmill CLI and a pre-initialised /home/user/myproject workspace folder whose wmill.yaml starts with an EMPTY excludes list."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - extra apt packages: jq (used by the verifier and to keep parity with other Windmill tasks)
#   - always required pip3 packages: pytest-json-ctrf
#   - extra pip3 packages: requests, PyYAML (used by both initial- and final-state tests)
#   - Node.js v24 + windmill-cli (`wmill` binary) for authoring/deploying/running scripts on the Windmill cloud
#   - /home/user/myproject: pre-initialised Windmill workspace folder with a default `wmill.yaml`
#     (`excludes: []` starts empty so the agent must add the protective glob themselves)
