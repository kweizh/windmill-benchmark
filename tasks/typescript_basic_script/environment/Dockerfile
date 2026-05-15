FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    npm install -g windmill-cli && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Windmill CLI task environment: Node.js v20, windmill-cli (wmill), and a scaffolded project directory at /home/user/windmill-project."

RUN mkdir -p /home/user/windmill-project

# Container contents:
#   - Node.js v20 and windmill-cli (wmill binary) installed globally via npm
#   - python3, python3-pip, python3-pytest for running test harness
#   - /home/user/windmill-project — empty scaffold directory for the Windmill project
#   - User must create f/scripts/greet.ts and f/scripts/greet.script.yaml

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
