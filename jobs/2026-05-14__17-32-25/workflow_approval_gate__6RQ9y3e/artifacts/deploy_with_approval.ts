import { task, workflow, waitForApproval } from "windmill-client";

async function runTests(branch: string): Promise<{
  branch: string;
  tests_passed: true;
  coverage: number;
}> {
  return { branch, tests_passed: true, coverage: 98 };
}

async function deployToProd(branch: string): Promise<{
  branch: string;
  status: string;
  url: string;
}> {
  return { branch, status: "deployed", url: "https://prod.example.com" };
}

export const main = workflow(async (branch: string) => {
  const testResult = await task(runTests)(branch);

  const approval = await waitForApproval({ timeout: 3600 });

  if (!approval.approved) {
    return {
      status: "rejected",
      approver: approval.approver,
      branch,
    };
  }

  const deployResult = await task(deployToProd)(branch);

  return {
    status: "deployed",
    ...deployResult,
    approver: approval.approver,
  };
});
