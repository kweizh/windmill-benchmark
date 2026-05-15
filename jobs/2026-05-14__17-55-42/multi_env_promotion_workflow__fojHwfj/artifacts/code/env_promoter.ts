// Windmill Workflow: Multi-Environment Promotion with Human Approval
// This workflow promotes a build artifact through dev -> staging -> production
// with human approval required between staging and production.

import { step, getResumeUrls, waitForApproval } from 'windmill';

interface ArtifactDeploymentInput {
  artifactId: string;
  version: string;
}

interface SuccessResult {
  promotionId: string;
  artifactId: string;
  version: string;
  status: 'promoted';
  environments: ['dev', 'staging', 'production'];
}

interface FailureResult {
  promotionId: string;
  status: 'failed';
  stoppedAt: 'dev' | 'staging' | 'production';
  error?: string;
}

interface RejectionResult {
  promotionId: string;
  status: 'rejected';
  stoppedAt: 'staging';
}

interface TestResult {
  passed: boolean;
}

export async function main(
  { artifactId, version }: ArtifactDeploymentInput
): Promise<SuccessResult | FailureResult | RejectionResult> {
  // Step 1: Generate promotion ID
  const promotionId = await step<string>(
    'generate-promotion-id',
    async () => {
      return `${artifactId}-${version}-${Date.now()}`;
    }
  );

  try {
    // Step 2: Deploy to dev environment
    const devDeployment = await step(
      'deploy-to-dev',
      async () => {
        return await $<string>({
          path: 'f/deploy_to_environment',
          args: {
            environment: 'dev',
            artifactId,
            version,
            promotionId,
          },
        });
      }
    );

    if (!devDeployment.success) {
      return {
        promotionId,
        status: 'failed',
        stoppedAt: 'dev',
        error: 'Dev deployment failed',
      };
    }

    // Step 3: Run integration tests against dev
    const devTests = await step<TestResult>(
      'run-dev-tests',
      async () => {
        return await $<TestResult>({
          path: 'f/run_integration_tests',
          args: {
            environment: 'dev',
            artifactId,
            version,
          },
        });
      }
    );

    if (!devTests.passed) {
      return {
        promotionId,
        status: 'failed',
        stoppedAt: 'dev',
        error: 'Dev integration tests failed',
      };
    }

    // Step 4: Deploy to staging environment
    try {
      await step(
        'deploy-to-staging',
        async () => {
          return await $<string>({
            path: 'f/deploy_to_environment',
            args: {
              environment: 'staging',
              artifactId,
              version,
              promotionId,
            },
          });
        }
      );
    } catch (error) {
      // Rollback staging on failure
      await step(
        'rollback-staging',
        async () => {
          return await $<void>({
            path: 'f/rollback_environment',
            args: {
              environment: 'staging',
              promotionId,
            },
          });
        }
      );

      return {
        promotionId,
        status: 'failed',
        stoppedAt: 'staging',
        error: 'Staging deployment failed',
      };
    }

    // Step 5: Run integration tests against staging
    const stagingTests = await step<TestResult>(
      'run-staging-tests',
      async () => {
        return await $<TestResult>({
          path: 'f/run_integration_tests',
          args: {
            environment: 'staging',
            artifactId,
            version,
          },
        });
      }
    );

    if (!stagingTests.passed) {
      // Rollback staging on test failure
      await step(
        'rollback-staging',
        async () => {
          return await $<void>({
            path: 'f/rollback_environment',
            args: {
              environment: 'staging',
              promotionId,
            },
          });
        }
      );

      return {
        promotionId,
        status: 'failed',
        stoppedAt: 'staging',
        error: 'Staging integration tests failed',
      };
    }

    // Step 6: Obtain approval URLs and log the approval page URL
    const approvalUrls = await step(
      'get-approval-urls',
      async () => {
        const urls = getResumeUrls();
        console.log('Approval page URL:', urls.approvalPage);
        return urls;
      }
    );

    // Step 7: Wait for approval (24 hours timeout)
    const approval = await waitForApproval({ timeout: 86400 });

    if (!approval.approved) {
      // Rollback staging on rejection
      await step(
        'rollback-staging',
        async () => {
          return await $<void>({
            path: 'f/rollback_environment',
            args: {
              environment: 'staging',
              promotionId,
            },
          });
        }
      );

      return {
        promotionId,
        status: 'rejected',
        stoppedAt: 'staging',
      };
    }

    // Step 8: Deploy to production environment
    try {
      await step(
        'deploy-to-production',
        async () => {
          return await $<string>({
            path: 'f/deploy_to_environment',
            args: {
              environment: 'production',
              artifactId,
              version,
              promotionId,
            },
          });
        }
      );
    } catch (error) {
      // Rollback production AND staging on failure
      await step(
        'rollback-production-and-staging',
        async () => {
          await $<void>({
            path: 'f/rollback_environment',
            args: {
              environment: 'production',
              promotionId,
            },
          });
          await $<void>({
            path: 'f/rollback_environment',
            args: {
              environment: 'staging',
              promotionId,
            },
          });
        }
      );

      return {
        promotionId,
        status: 'failed',
        stoppedAt: 'production',
        error: 'Production deployment failed',
      };
    }

    // Step 9: Run smoke tests against production
    const productionTests = await step<TestResult>(
      'run-production-smoke-tests',
      async () => {
        return await $<TestResult>({
          path: 'f/run_smoke_tests',
          args: {
            environment: 'production',
            artifactId,
            version,
          },
        });
      }
    );

    if (!productionTests.passed) {
      // Rollback production AND staging on test failure
      await step(
        'rollback-production-and-staging',
        async () => {
          await $<void>({
            path: 'f/rollback_environment',
            args: {
              environment: 'production',
              promotionId,
            },
          });
          await $<void>({
            path: 'f/rollback_environment',
            args: {
              environment: 'staging',
              promotionId,
            },
          });
        }
      );

      return {
        promotionId,
        status: 'failed',
        stoppedAt: 'production',
        error: 'Production smoke tests failed',
      };
    }

    // Step 10: Full success - return success object
    return {
      promotionId,
      artifactId,
      version,
      status: 'promoted',
      environments: ['dev', 'staging', 'production'],
    };

  } catch (error) {
    // Catch-all for unexpected errors
    return {
      promotionId,
      status: 'failed',
      stoppedAt: 'dev',
      error: error instanceof Error ? error.message : 'Unknown error occurred',
    };
  }
}