FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
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

# Create the broken cached_enricher.ts workflow file (missing cache_ttl — to be fixed by the agent)
RUN cat > /home/user/windmill-project/f/workflows/cached_enricher.ts << 'EOF'
import { task, workflow, parallel } from 'windmill-client';

async function enrichRecord(record: { id: string, name: string }) {
  // Simulates an expensive external API call
  console.log(`Enriching record: ${record.id}`);
  return { ...record, enriched: true, score: record.name.length * 10 };
}

async function saveResults(results: any[]) {
  console.log(`Saving ${results.length} enriched records`);
  return { saved: results.length };
}

export const main = workflow(async (records: Array<{ id: string, name: string }>) => {
  // BUG: No caching - same records are enriched repeatedly on every run
  const enriched = await parallel(records, (record) => task(enrichRecord)(record));
  return await task(saveResults)(enriched);
});
EOF

WORKDIR /home/user/windmill-project
