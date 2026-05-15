FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    curl \
    wget \
    ca-certificates \
    git \
    python3 \
    python3-pip \
    python3-pytest \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js v20 via NodeSource
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Windmill CLI (installs as `wmill`)
RUN npm install -g windmill-cli

# Create user home directory
RUN mkdir -p /home/user

# Create the Windmill project directory structure
RUN mkdir -p /home/user/windmill-project/f/workflows

# Write the broken reminder.ts using a heredoc
RUN cat > /home/user/windmill-project/f/workflows/reminder.ts <<'EOF'
import { task, workflow } from 'windmill-client';

async function sendAlert(message: string) {
  console.log(`ALERT: ${message}`);
  return 'alert_sent';
}

async function sendFollowUp(message: string) {
  console.log(`FOLLOW-UP: ${message}`);
  return 'followup_sent';
}

export const main = workflow(async (message: string, delay_seconds: number) => {
  await task(sendAlert)(message);
  // BUG: This blocks the worker thread instead of releasing it
  await new Promise(resolve => setTimeout(resolve, delay_seconds * 1000));
  await task(sendFollowUp)(message);
  return 'done';
});
EOF

WORKDIR /home/user/windmill-project
