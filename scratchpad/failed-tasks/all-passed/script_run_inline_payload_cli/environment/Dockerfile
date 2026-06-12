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

# Stash the bootstrap assets used to deploy the addition script during the
# initial-state setup phase (see environment/test_initial_state.py). These
# files are NOT meant to be touched or read by the agent during the task.
RUN mkdir -p /opt/wmill_bootstrap/f/zealt_eval && \
    printf '%s\n' \
        'def main(a: int, b: int):' \
        '    return a + b' \
        > /opt/wmill_bootstrap/f/zealt_eval/add_numbers.py

LABEL Author="generate-harbor-tasks"
LABEL Description="Windmill CLI environment for invoking a pre-deployed addition script on Windmill Cloud."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - Node.js v24 (required by the Windmill CLI)
#   - Windmill CLI (`wmill`) installed globally via `npm install -g windmill-cli`
#   - python3 `requests` library used by test_initial_state.py for API-based script deployment
#   - /home/user: working directory for the agent
#   - /opt/wmill_bootstrap/f/zealt_eval/add_numbers.py: the addition script body used to seed the workspace during initial-state setup
