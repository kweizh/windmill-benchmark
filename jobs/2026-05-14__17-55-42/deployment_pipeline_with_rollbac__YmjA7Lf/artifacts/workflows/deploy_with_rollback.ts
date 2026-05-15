import { task, workflow, step, waitForApproval } from 'windmill-client';
import crypto from 'node:crypto';

async function runTests(branch: string) {
  return { branch, passed: true, tests: 42 };
}

async function deployToStaging(branch: string, deployId: string) {
  return { deployId, env: 'staging', url: 'https://staging.example.com' };
}

async function rollbackStaging(deployId: string) {
  return { deployId, rolled_back: 'staging' };
}

async function deployToProduction(branch: string, deployId: string) {
  return { deployId, env: 'production', url: 'https://prod.example.com' };
}

async function rollbackProduction(deployId: string) {
  return { deployId, rolled_back: 'production' };
}

export const main = workflow('deploy_with_rollback', async (branch: string) => {
  const deployId = await step('deploy_id', () => crypto.randomUUID());

  const testResult = await task(runTests)(branch);
  if (!testResult.passed) {
    throw new Error('Tests failed');
  }

  try {
    await task(deployToStaging)(branch, deployId);
  } catch (e) {
    await task(rollbackStaging)(deployId);
    throw e;
  }

  const approval = await waitForApproval({ timeout: 7200 });
  if (!approval.approved) {
    await task(rollbackStaging)(deployId);
    return { deployId, status: 'rejected', branch, approver: approval.approver };
  }

  try {
    await task(deployToProduction)(branch, deployId);
  } catch (e) {
    await task(rollbackProduction)(deployId);
    throw e;
  }

  return { deployId, status: 'deployed', branch, approver: approval.approver };
});