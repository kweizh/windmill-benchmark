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
LABEL Description="Windmill heartbeat script task: fix get_state/set_state usage in /home/user/windmill-project/f/monitoring/heartbeat.py"

RUN mkdir -p /home/user/windmill-project/f/monitoring && \
    cat > /home/user/windmill-project/f/monitoring/heartbeat.py <<'EOF'
import time

def main():
    # TODO: Fix this script to use Windmill state to track execution count
    count = 0  # BUG: This resets every run!
    count += 1
    return {
        "count": count,
        "timestamp": time.time(),
        "message": f"Heartbeat #{count}"
    }
EOF

# Container contents:
#   - python3, pip3, python3-pytest installed via apt
#   - Node.js v20 + windmill-cli (wmill) installed via npm
#   - wmill Python package installed via pip3
#   - /home/user/windmill-project/f/monitoring/heartbeat.py — broken heartbeat script with count = 0 reset bug

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
