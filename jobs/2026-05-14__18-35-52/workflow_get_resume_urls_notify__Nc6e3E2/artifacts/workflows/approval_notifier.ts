import {
  getResumeUrls,
  step,
  task,
  workflow,
  waitForApproval,
} from 'windmill-client';

async function deploy(target: string) {
  console.log(`Deploying to ${target}`);
  return { target, status: 'deployed', timestamp: new Date().toISOString() };
}

export const main = workflow(async (target: string) => {
  const urls = await step('approval_urls', () => getResumeUrls());
  await step('log_approval_url', () =>
    console.log(`Approval required. Visit: ${urls.approvalPage}`),
  );
  const approval = await waitForApproval({ timeout: 7200 });
  if (!approval.approved) {
    return { status: 'rejected', approver: approval.approver };
  }
  return await task(deploy)(target);
});
