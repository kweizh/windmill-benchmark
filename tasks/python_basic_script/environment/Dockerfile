FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-pytest bash && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    npm install -g windmill-cli && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Windmill Python script task environment with Node.js v24, wmill CLI, and python3."

RUN mkdir -p /home/user/windmill-project/f/scripts

# Container contents:
#   - python3, python3-pip, python3-pytest — for running Python Windmill scripts
#   - Node.js v24 + wmill CLI — Windmill CLI tooling
#   - /home/user/windmill-project/f/scripts/ — empty scripts directory

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
