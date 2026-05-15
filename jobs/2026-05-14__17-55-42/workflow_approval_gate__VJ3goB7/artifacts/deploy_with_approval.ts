import { task, workflow, waitForApproval } from 'windmill-client';

// Task function to run tests
export async function runTests(branch: string) {
  return {
    branch,
    tests_passed: true,
    coverage: 98
  };
}

// Task function to deploy to production
export async function deployToProd(branch: string) {
  return {
    branch,
    status: 'deployed' as const,
    url: 'https://prod.example.com'
  };
}

// Main workflow with approval gate
export async function main(branch: string) {
  // Run tests and store result
  const testResult = await task(runTests)(branch);
  
  // Wait for human approval (1 hour timeout)
  const approval = await waitForApproval({ timeout: 3600 });
  
  // Check if approval was granted
  if (!approval.approved) {
    return {
      status: 'rejected' as const,
      approver: approval.approver,
      branch
    };
  }
  
  // Deploy to production if approved
  const deployResult = await task(deployToProd)(branch);
  
  return {
    status: 'deployed' as const,
    ...deployResult,
    approver: approval.approver
  };
}

// Export as workflow
export default workflow(main);