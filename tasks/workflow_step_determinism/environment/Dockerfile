FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
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
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Windmill CLI (provides the `wmill` binary)
RUN npm install -g windmill-cli

# Create home user directory
RUN mkdir -p /home/user

# Create windmill project structure
RUN mkdir -p /home/user/windmill-project/f/workflows

# Write the broken order_processor.ts with non-deterministic calls outside step()
RUN cat > /home/user/windmill-project/f/workflows/order_processor.ts << 'EOF'
import { task, workflow } from 'windmill-client';

async function processOrder(orderId: string, timestamp: number, product: string) {
  console.log(`Processing order ${orderId} for ${product} at ${timestamp}`);
  return { orderId, product, status: 'processed' };
}

async function notifyShipping(orderId: string, product: string) {
  console.log(`Shipping notification sent for order ${orderId}: ${product}`);
  return 'notification_sent';
}

export const main = workflow(async (product: string) => {
  // BUG: Non-deterministic calls directly in workflow body - will break on replay
  const timestamp = Date.now();
  const orderId = Math.random().toString(36).slice(2);
  
  const result = await task(processOrder)(orderId, timestamp, product);
  await task(notifyShipping)(orderId, product);
  return result;
});
EOF

WORKDIR /home/user/windmill-project
