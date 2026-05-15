FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# System dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    gnupg \
    python3 \
    python3-pip \
    python3-pytest \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js v20 via NodeSource
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Windmill CLI
RUN npm install -g windmill-cli

# Create the windmill project directory structure
RUN mkdir -p /home/user/windmill-project/f/workflows

# Write the broken approval_notifier.ts via heredoc
RUN cat > /home/user/windmill-project/f/workflows/approval_notifier.ts << 'EOF'
import { task, workflow, waitForApproval } from 'windmill-client';

async function deploy(target: string) {
  console.log(`Deploying to ${target}`);
  return { target, status: 'deployed', timestamp: new Date().toISOString() };
}

export const main = workflow(async (target: string) => {
  const approval = await waitForApproval({ timeout: 7200 });
  if (!approval.approved) {
    return { status: 'rejected', approver: approval.approver };
  }
  return await task(deploy)(target);
});
EOF

WORKDIR /home/user/windmill-project
