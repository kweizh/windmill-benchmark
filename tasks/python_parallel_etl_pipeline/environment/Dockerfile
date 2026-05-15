FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash && \
    pip3 install --break-system-packages wmill && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    npm install -g windmill-cli && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Python Windmill ETL pipeline task — agent must create etl_pipeline.py with parallel extract/transform/load."

RUN mkdir -p /home/user/windmill-project/f/workflows

# Container contents:
#   - python3, python3-pip, python3-pytest
#   - wmill Python package (pip)
#   - Node.js v20 + windmill-cli npm package (wmill CLI)
#   - /home/user/windmill-project/f/workflows/ directory scaffold
#   - etl_pipeline.py intentionally absent (agent must create it)

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
