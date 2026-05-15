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
LABEL Description="Windmill CLI environment for writing TypeScript scripts with typed resource parameters."

RUN mkdir -p /home/user/windmill-project/f/scripts

# Container contents:
#   - Node.js v20 and npm
#   - windmill-cli (wmill) installed globally via npm
#   - python3, python3-pip, python3-pytest for test harness
#   - /home/user/windmill-project          — pre-created project root
#   - /home/user/windmill-project/f/scripts — script directory ready for use

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
