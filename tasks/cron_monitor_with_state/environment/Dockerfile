FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# ── System dependencies ────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    ca-certificates \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# ── Node.js v20 via NodeSource ────────────────────────────────────────────────
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# ── Windmill CLI (wmill) via npm ──────────────────────────────────────────────
RUN npm install -g windmill-cli

# ── Python: wmill package ─────────────────────────────────────────────────────
RUN pip3 install --break-system-packages wmill

# ── Windmill project directory structure ──────────────────────────────────────
RUN mkdir -p /home/user/windmill-project/f/scripts

# ── Broken health_monitor.py (initial state for the agent to fix) ─────────────
RUN cat > /home/user/windmill-project/f/scripts/health_monitor.py << 'PYEOF'
import urllib.request
from wmill import set_state

def check_endpoint(url: str) -> str:
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            return 'healthy' if response.status == 200 else 'degraded'
    except Exception:
        return 'down'

def send_alert(service: str, status: str):
    print(f"ALERT: {service} is {status}")

def main(service_url: str = "https://httpbin.org/status/200", service_name: str = "MyService"):
    # BUG: No get_state() - cannot detect status changes
    current_status = check_endpoint(service_url)
    # BUG: Always sends alert on every run, not just on change
    send_alert(service_name, current_status)
    set_state(current_status)
    return {'status': current_status, 'alerted': True}
PYEOF

WORKDIR /home/user/windmill-project
