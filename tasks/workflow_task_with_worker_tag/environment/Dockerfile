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

# Write the broken ml_pipeline.ts — trainModel has no worker tag (the bug)
RUN cat > /home/user/windmill-project/f/workflows/ml_pipeline.ts << 'EOF'
import { task, workflow } from 'windmill-client';

async function preprocessData(data: number[]) {
  console.log(`Preprocessing ${data.length} data points`);
  return { normalized: data.map(x => x / 100), count: data.length };
}

async function trainModel(data: { normalized: number[], count: number }) {
  console.log(`Training model on ${data.count} samples`);
  return { model_id: 'ml-model-v1', accuracy: 0.95, trained_on: data.count };
}

export const main = workflow(async (rawData: number[]) => {
  // Preprocessing can run on any worker
  const processedData = await task(preprocessData)(rawData);
  // BUG: Model training should be routed to GPU workers but has no tag
  const modelResult = await task(trainModel)(processedData);
  return modelResult;
});
EOF

WORKDIR /home/user/windmill-project
