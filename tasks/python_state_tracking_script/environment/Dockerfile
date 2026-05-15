FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    npm install -g windmill-cli && \
    pip3 install --break-system-packages wmill && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Windmill Python state tracking task environment with wmill CLI and Python package installed."

RUN mkdir -p /home/user/windmill-project/f/scripts

# Container contents:
#   - python3, pip3, python3-pytest, curl, wget, ca-certificates, git, bash
#   - Node.js v20 (required by windmill-cli)
#   - windmill-cli installed globally via npm (provides the 'wmill' binary)
#   - wmill Python package installed via pip3 (provides 'from wmill import get_state, set_state')
#   - /home/user/windmill-project  — pre-created Windmill project root
#   - /home/user/windmill-project/f/scripts  — scripts subdirectory (empty, user must populate)

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
