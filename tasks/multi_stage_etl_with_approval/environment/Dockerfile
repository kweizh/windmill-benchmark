FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl \
        wget \
        ca-certificates \
        git \
        python3 \
        python3-pip \
        python3-pytest \
        bash && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    npm install -g windmill-cli && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Windmill multi-stage ETL + approval workflow task environment with Node.js v20 and windmill-cli."

# Create the project structure expected by the initial state tests.
# The target file etl_with_approval.ts is intentionally NOT created here —
# the agent is expected to author it.
RUN mkdir -p /home/user/windmill-project/f/workflows

# Container contents:
#   - Node.js v20 installed via NodeSource
#   - windmill-cli installed globally (provides the wmill binary)
#   - /home/user/windmill-project/f/workflows  — empty directory ready for the workflow file
#   - etl_with_approval.ts is NOT present (agent must create it)

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
