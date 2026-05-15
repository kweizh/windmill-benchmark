import { step, getResumeUrls, waitForApproval, task } from "windmill-client";

export async function main(artifactId: string, version: string) {
  // 2. Generate a promotion ID using step()
  const promotionId = await step("generate_promotion_id", async () => {
    return `promo-${artifactId}-${version}-${Date.now()}`;
  });

  // 3. Deploy to dev environment using a task. If it fails, immediately return a failure object.
  try {
    await task("f/deploy", { env: "dev", artifactId, version });
  } catch (error) {
    return { promotionId, status: "failed", stoppedAt: "dev", error: String(error) };
  }

  // 4. Run integration tests against dev using a task. If tests fail (returns { passed: false }), return a failure object.
  try {
    const testResult = await task("f/integration_tests", { env: "dev", artifactId, version });
    if (testResult && testResult.passed === false) {
      return { promotionId, status: "failed", stoppedAt: "dev_tests", error: "Integration tests failed" };
    }
  } catch (error) {
    return { promotionId, status: "failed", stoppedAt: "dev_tests", error: String(error) };
  }

  // 5. Deploy to staging environment using a task. Wrap in try/catch — on failure, rollback staging and return a failure object.
  try {
    await task("f/deploy", { env: "staging", artifactId, version });
  } catch (error) {
    try {
      await task("f/rollback", { env: "staging", artifactId, version });
    } catch (rollbackError) {}
    return { promotionId, status: "failed", stoppedAt: "staging", error: String(error) };
  }

  // 6. Obtain approval URLs using getResumeUrls() inside a step(). Log the approval page URL.
  await step("get_approval_urls", async () => {
    const urls = await getResumeUrls();
    console.log("Approval page URL:", urls.approvalPage);
    return urls;
  });

  // 7. Wait for approval using waitForApproval({ timeout: 86400 }) (24 hours). 
  // On rejection, rollback staging and return a rejection object with { promotionId, status: 'rejected', stoppedAt: 'staging' }.
  try {
    const approval = await waitForApproval({ timeout: 86400 });
    if (approval && (approval === false || approval.rejected === true || approval.status === 'rejected')) {
      throw new Error("Rejected");
    }
  } catch (error) {
    try {
      await task("f/rollback", { env: "staging", artifactId, version });
    } catch (rollbackError) {}
    return { promotionId, status: "rejected", stoppedAt: "staging" };
  }

  // 8. Deploy to production environment using a task. Wrap in try/catch — on failure, rollback production AND staging, and return a failure object.
  try {
    await task("f/deploy", { env: "production", artifactId, version });
  } catch (error) {
    try {
      await task("f/rollback", { env: "production", artifactId, version });
    } catch (rollbackError) {}
    try {
      await task("f/rollback", { env: "staging", artifactId, version });
    } catch (rollbackError) {}
    return { promotionId, status: "failed", stoppedAt: "production", error: String(error) };
  }

  // 9. On full success, return { promotionId, artifactId, version, status: 'promoted', environments: ['dev', 'staging', 'production'] }.
  return { 
    promotionId, 
    artifactId, 
    version, 
    status: "promoted", 
    environments: ["dev", "staging", "production"] 
  };
}
