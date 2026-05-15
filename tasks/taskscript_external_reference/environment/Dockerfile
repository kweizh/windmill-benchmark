FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install the Windmill CLI (wmill)
RUN npm install -g windmill-cli

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Windmill WAC task environment with wmill CLI and Node.js v20; contains a broken data_orchestrator.ts that uses inline task() calls instead of taskScript() references."

# Create the Windmill project scaffold
RUN mkdir -p /home/user/windmill-project && \
    cd /home/user/windmill-project && \
    cat >wmill.yaml <<'EOF'
defaultTs: bun
EOF

# Pre-install windmill-client so the agent can run/type-check locally
RUN cd /home/user/windmill-project && \
    npm init -y && \
    npm install windmill-client

# Create the workflows directory and the broken data_orchestrator.ts
RUN mkdir -p /home/user/windmill-project/f/workflows && \
    cat >/home/user/windmill-project/f/workflows/data_orchestrator.ts <<'EOF'
import { task, workflow } from 'windmill-client';

async function extractUsers(params: { limit: number }) {
  console.log(`Extracting ${params.limit} users`);
  return Array.from({ length: params.limit }, (_, i) => ({ id: i + 1, name: `User ${i + 1}` }));
}

async function transformRecords(params: { records: any[] }) {
  return params.records.map(r => ({ ...r, transformed: true, timestamp: new Date().toISOString() }));
}

async function saveResults(results: any[]) {
  console.log(`Saving ${results.length} results`);
  return { saved: results.length, status: 'success' };
}

export const main = workflow(async (limit: number) => {
  const users = await task(extractUsers)({ limit });
  const transformed = await task(transformRecords)({ records: users });
  return await task(saveResults)(transformed);
});
EOF

# Container contents:
#   - curl, wget, ca-certificates, git, python3, python3-pip, python3-pytest, bash
#   - Node.js v20 (via nodesource)
#   - wmill CLI at /usr/local/bin/wmill
#   - /home/user/windmill-project  — Windmill project root with wmill.yaml
#   - windmill-client npm package installed in the project
#   - /home/user/windmill-project/f/workflows/data_orchestrator.ts  — broken file
#     with inline extractUsers and transformRecords task functions (to be refactored)

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
