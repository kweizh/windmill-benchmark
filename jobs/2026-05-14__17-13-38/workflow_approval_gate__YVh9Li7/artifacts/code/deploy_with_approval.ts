import { task, workflow, waitForApproval } from "windmill-client";

export async function runTests(branch: string) {
  return { branch, tests_passed: true, coverage: 98 };
}

export async function deployToProd(branch: string) {
  return { branch, status: 'deployed', url: 'https://prod.example.com' };
}

export const main = workflow(async function (branch: string) {
  const testResult = await task(runTests)(branch);
  
  const approval = await waitForApproval({ timeout: 3600 });
  
  if (!approval.approved) {
    return { status: 'rejected', approver: approval.approver, branch };
  }
  
  const deployResult = await task(deployToProd)(branch);
  
  return { status: 'deployed', ...deployResult, approver: approval.approver };
});
