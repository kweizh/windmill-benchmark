import * as wmill from "windmill-client";

/**
 * Promotes a build artifact through multiple environments with human approval.
 * 
 * @param artifactId The ID of the artifact to promote.
 * @param version The version of the artifact to promote.
 */
export async function main(artifactId: string, version: string) {
  // 2. Generate a promotion ID using step()
  const promotionId = await wmill.step(async () => {
    return `PROMO-${Math.random().toString(36).substring(2, 9).toUpperCase()}`;
  });

  // 3. Deploy to dev environment using a task. If it fails, immediately return a failure object.
  try {
    await wmill.step(async () => {
      console.log(`Deploying ${artifactId}:${version} to dev`);
      // Simulation of deployment logic
    });
  } catch (error) {
    return { 
      promotionId, 
      artifactId, 
      version, 
      status: 'failed', 
      environment: 'dev', 
      error: error instanceof Error ? error.message : String(error) 
    };
  }

  // 4. Run integration tests against dev using a task. 
  // If tests fail (returns { passed: false }), return a failure object.
  const testResults = await wmill.step(async () => {
    console.log(`Running integration tests on dev for ${artifactId}:${version}`);
    // Simulation of test logic
    // In a real scenario, this would perform actual HTTP requests or CLI commands
    return { passed: true }; 
  });

  if (!testResults.passed) {
    return { 
      promotionId, 
      artifactId, 
      version, 
      status: 'failed', 
      environment: 'dev', 
      error: 'Integration tests failed' 
    };
  }

  // 5. Deploy to staging environment using a task. 
  // Wrap in try/catch — on failure, rollback staging and return a failure object.
  try {
    await wmill.step(async () => {
      console.log(`Deploying ${artifactId}:${version} to staging`);
      // Simulation of staging deployment
    });
  } catch (error) {
    await rollback('staging', artifactId, version);
    return { 
      promotionId, 
      artifactId, 
      version, 
      status: 'failed', 
      environment: 'staging', 
      error: error instanceof Error ? error.message : String(error) 
    };
  }

  // 6. Obtain approval URLs using getResumeUrls() inside a step(). Log the approval page URL.
  await wmill.step(async () => {
    const urls = await wmill.getResumeUrls();
    console.log(`Approval page URL: ${urls.approvalPage}`);
  });

  // 7. Wait for approval using waitForApproval({ timeout: 86400 }) (24 hours). 
  // On rejection, rollback staging and return a rejection object.
  try {
    await wmill.waitForApproval({ timeout: 86400 });
  } catch (error) {
    // On rejection or timeout, rollback staging
    await rollback('staging', artifactId, version);
    return { 
      promotionId, 
      status: 'rejected', 
      stoppedAt: 'staging' 
    };
  }

  // 8. Deploy to production environment using a task. 
  // Wrap in try/catch — on failure, rollback production AND staging, and return a failure object.
  try {
    await wmill.step(async () => {
      console.log(`Deploying ${artifactId}:${version} to production`);
      // Simulation of production deployment
    });
  } catch (error) {
    await rollback('production', artifactId, version);
    await rollback('staging', artifactId, version);
    return { 
      promotionId, 
      artifactId, 
      version, 
      status: 'failed', 
      environment: 'production', 
      error: error instanceof Error ? error.message : String(error) 
    };
  }

  // 9. On full success, return success object.
  return { 
    promotionId, 
    artifactId, 
    version, 
    status: 'promoted', 
    environments: ['dev', 'staging', 'production'] 
  };
}

/**
 * Helper function to simulate rollback of an environment.
 */
async function rollback(env: string, artifactId: string, version: string) {
  await wmill.step(async () => {
    console.log(`Rolling back ${env} for ${artifactId}:${version}`);
    // Simulation of rollback logic
  });
}
