FROM ubuntu:24.04

ENV HOME=/home/user
ENV PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    npm i -g windmill-cli && \
    pip3 install --break-system-packages pytest-json-ctrf requests && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /home/user/wac-pipeline && chmod 0755 /home/user/wac-pipeline

LABEL Author="generate-harbor-tasks"
LABEL Description="Windmill WAC approval/resume task environment: Ubuntu 24.04 with Node.js v24, windmill-cli, python3 / pytest / requests."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - Node.js v24 (required by windmill-cli, which needs Node >= 20)
#   - windmill-cli (`wmill`) installed globally via npm for deploying WAC scripts
#   - python3 `requests` for the verifier's HTTP calls against the Windmill API
#   - /home/user/wac-pipeline: agent's empty project directory; the agent will
#     create `f/eval/deploy_pipeline_<run-id>.ts` and the matching
#     `.script.yaml` companion file here, then `wmill sync push --yes` (or
#     `wmill script push`) to deploy to https://app.windmill.dev
