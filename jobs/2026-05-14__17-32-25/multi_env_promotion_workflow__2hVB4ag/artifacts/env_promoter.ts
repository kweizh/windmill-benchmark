/**
 * Multi-Environment Promotion Workflow
 *
 * Promotes a build artifact through dev → staging → production with a
 * human-approval gate between staging and production.
 *
 * Parameters
 * ----------
 * artifactId : string  – unique identifier of the build artifact
 * version    : string  – semantic version string of the artifact
 */

import * as wmill from "windmill-client";

// ---------------------------------------------------------------------------
// Type definitions
// ---------------------------------------------------------------------------

interface DeployResult {
  success: boolean;
  environment: string;
  message?: string;
}

interface TestResult {
  passed: boolean;
  details?: string;
}

interface SuccessResult {
  promotionId: string;
  artifactId: string;
  version: string;
  status: "promoted";
  environments: ["dev", "staging", "production"];
}

interface FailureResult {
  promotionId: string;
  artifactId: string;
  version: string;
  status: "failed" | "rejected";
  stoppedAt: "dev" | "staging" | "production";
  reason?: string;
}

// ---------------------------------------------------------------------------
// Helper task wrappers
// ---------------------------------------------------------------------------

/**
 * Deploy artifact to the specified environment.
 * Maps to a Windmill task script path: `f/tasks/deploy_to_env`.
 */
async function deployToEnv(
  artifactId: string,
  version: string,
  environment: string
): Promise<DeployResult> {
  return await wmill.task("f/tasks/deploy_to_env", {
    artifactId,
    version,
    environment,
  });
}

/**
 * Run integration tests against the specified environment.
 * Maps to a Windmill task script path: `f/tasks/run_integration_tests`.
 */
async function runIntegrationTests(
  artifactId: string,
  version: string,
  environment: string
): Promise<TestResult> {
  return await wmill.task("f/tasks/run_integration_tests", {
    artifactId,
    version,
    environment,
  });
}

/**
 * Roll back the artifact in the specified environment.
 * Maps to a Windmill task script path: `f/tasks/rollback_env`.
 */
async function rollbackEnv(
  artifactId: string,
  version: string,
  environment: string
): Promise<void> {
  await wmill.task("f/tasks/rollback_env", {
    artifactId,
    version,
    environment,
  });
}

// ---------------------------------------------------------------------------
// Main workflow export
// ---------------------------------------------------------------------------

export async function main(
  artifactId: string,
  version: string
): Promise<SuccessResult | FailureResult> {
  // ── Step 1: Generate a unique promotion ID ──────────────────────────────
  const promotionId: string = await wmill.step(async () => {
    const timestamp = Date.now();
    const random = Math.random().toString(36).slice(2, 8).toUpperCase();
    return `PROMO-${timestamp}-${random}`;
  });

  console.log(
    `[${promotionId}] Starting promotion of artifact "${artifactId}" @ v${version}`
  );

  // ── Step 2: Deploy to dev ───────────────────────────────────────────────
  console.log(`[${promotionId}] Deploying to dev...`);
  const devDeploy: DeployResult = await wmill.task("f/tasks/deploy_to_env", {
    artifactId,
    version,
    environment: "dev",
  });

  if (!devDeploy.success) {
    console.error(
      `[${promotionId}] Dev deployment failed: ${devDeploy.message ?? "unknown error"}`
    );
    return {
      promotionId,
      artifactId,
      version,
      status: "failed",
      stoppedAt: "dev",
      reason: devDeploy.message ?? "Dev deployment failed",
    };
  }

  console.log(`[${promotionId}] Dev deployment succeeded.`);

  // ── Step 3: Run integration tests against dev ───────────────────────────
  console.log(`[${promotionId}] Running integration tests on dev...`);
  const testResult: TestResult = await wmill.task(
    "f/tasks/run_integration_tests",
    {
      artifactId,
      version,
      environment: "dev",
    }
  );

  if (!testResult.passed) {
    console.error(
      `[${promotionId}] Integration tests failed on dev: ${testResult.details ?? "no details"}`
    );
    return {
      promotionId,
      artifactId,
      version,
      status: "failed",
      stoppedAt: "dev",
      reason: `Integration tests failed: ${testResult.details ?? "no details"}`,
    };
  }

  console.log(`[${promotionId}] Integration tests passed on dev.`);

  // ── Step 4: Deploy to staging ───────────────────────────────────────────
  console.log(`[${promotionId}] Deploying to staging...`);
  let stagingDeploy: DeployResult;

  try {
    stagingDeploy = await wmill.task("f/tasks/deploy_to_env", {
      artifactId,
      version,
      environment: "staging",
    });

    if (!stagingDeploy.success) {
      throw new Error(stagingDeploy.message ?? "Staging deployment returned failure");
    }
  } catch (err: unknown) {
    const reason = err instanceof Error ? err.message : String(err);
    console.error(`[${promotionId}] Staging deployment failed: ${reason}. Rolling back...`);

    await rollbackEnv(artifactId, version, "staging");
    console.log(`[${promotionId}] Staging rollback complete.`);

    return {
      promotionId,
      artifactId,
      version,
      status: "failed",
      stoppedAt: "staging",
      reason,
    };
  }

  console.log(`[${promotionId}] Staging deployment succeeded.`);

  // ── Step 5: Obtain approval URLs and wait for human approval ────────────
  const approvalUrls = await wmill.step(async () => {
    const urls = await wmill.getResumeUrls();
    console.log(
      `[${promotionId}] Approval required. Visit the approval page:\n  ${urls.approvalPage}`
    );
    return urls;
  });

  console.log(`[${promotionId}] Waiting for approval (timeout: 24 h)...`);
  let approved: boolean;

  try {
    const approvalPayload = await wmill.waitForApproval({ timeout: 86400 });
    // waitForApproval resolves with the payload on approval, throws on rejection/timeout.
    approved = true;
    console.log(
      `[${promotionId}] Promotion approved.`,
      approvalPayload ?? ""
    );
  } catch (approvalErr: unknown) {
    const reason =
      approvalErr instanceof Error ? approvalErr.message : String(approvalErr);
    console.warn(
      `[${promotionId}] Promotion rejected or timed out: ${reason}. Rolling back staging...`
    );

    await rollbackEnv(artifactId, version, "staging");
    console.log(`[${promotionId}] Staging rollback complete after rejection.`);

    return {
      promotionId,
      artifactId,
      version,
      status: "rejected",
      stoppedAt: "staging",
    };
  }

  // ── Step 6: Deploy to production ────────────────────────────────────────
  console.log(`[${promotionId}] Deploying to production...`);

  try {
    const prodDeploy: DeployResult = await wmill.task("f/tasks/deploy_to_env", {
      artifactId,
      version,
      environment: "production",
    });

    if (!prodDeploy.success) {
      throw new Error(prodDeploy.message ?? "Production deployment returned failure");
    }
  } catch (err: unknown) {
    const reason = err instanceof Error ? err.message : String(err);
    console.error(
      `[${promotionId}] Production deployment failed: ${reason}. Rolling back production and staging...`
    );

    // Roll back both production and staging in parallel for speed.
    await Promise.all([
      rollbackEnv(artifactId, version, "production"),
      rollbackEnv(artifactId, version, "staging"),
    ]);

    console.log(
      `[${promotionId}] Production and staging rollbacks complete.`
    );

    return {
      promotionId,
      artifactId,
      version,
      status: "failed",
      stoppedAt: "production",
      reason,
    };
  }

  console.log(`[${promotionId}] Production deployment succeeded.`);

  // ── Step 7: Return full-success result ───────────────────────────────────
  const result: SuccessResult = {
    promotionId,
    artifactId,
    version,
    status: "promoted",
    environments: ["dev", "staging", "production"],
  };

  console.log(`[${promotionId}] Promotion complete.`, result);
  return result;
}
