# Multi-Environment Promotion Workflow

## Overview

This Windmill workflow (`env_promoter.ts`) promotes a build artifact through multiple environments (dev → staging → production) with human approval required between staging and production deployment.

## Features

- **Automated deployment**: Sequential deployment through dev, staging, and production environments
- **Automated testing**: Integration tests run after each deployment
- **Human approval gate**: Manual approval required before production deployment
- **Automatic rollback**: Failed deployments trigger automatic rollbacks
- **Comprehensive error handling**: Detailed failure tracking with environment-specific error messages

## Workflow Steps

1. **Generate Promotion ID**: Creates a unique identifier for the promotion using `step()`

2. **Deploy to Dev**: 
   - Deploys artifact to dev environment
   - Returns failure object if deployment fails

3. **Run Dev Tests**: 
   - Executes integration tests against dev
   - Returns failure object if tests fail (`{ passed: false }`)

4. **Deploy to Staging**: 
   - Wraps deployment in try/catch
   - On failure: rolls back staging and returns failure object

5. **Run Staging Tests**: 
   - Executes integration tests against staging
   - On failure: rolls back staging and returns failure object

6. **Obtain Approval URLs**: 
   - Uses `getResumeUrls()` inside a `step()`
   - Logs the approval page URL

7. **Wait for Approval**: 
   - Uses `waitForApproval({ timeout: 86400 })` (24 hours)
   - On rejection: rolls back staging and returns rejection object with `{ promotionId, status: 'rejected', stoppedAt: 'staging' }`

8. **Deploy to Production**: 
   - Wraps deployment in try/catch
   - On failure: rolls back production AND staging, returns failure object

9. **Run Production Tests**: 
   - Executes smoke tests against production
   - On failure: rolls back production AND staging, returns failure object

10. **Complete Success**: 
    - Returns `{ promotionId, artifactId, version, status: 'promoted', environments: ['dev', 'staging', 'production'] }`

## Input Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `artifactId` | `string` | The identifier of the artifact to promote |
| `version` | `string` | The version of the artifact to promote |

## Return Types

### Success Result
```typescript
{
  promotionId: string;
  artifactId: string;
  version: string;
  status: 'promoted';
  environments: ['dev', 'staging', 'production'];
}
```

### Failure Result
```typescript
{
  promotionId: string;
  status: 'failed';
  stoppedAt: 'dev' | 'staging' | 'production';
  error?: string;
}
```

### Rejection Result
```typescript
{
  promotionId: string;
  status: 'rejected';
  stoppedAt: 'staging';
}
```

## Dependencies

The workflow expects the following Windmill tasks to exist:

- `f/deploy_to_environment` - Deploys an artifact to a specific environment
- `f/run_integration_tests` - Runs integration tests against an environment
- `f/run_smoke_tests` - Runs smoke tests against an environment
- `f/rollback_environment` - Rolls back an environment to a previous state

## Usage Example

```typescript
// Trigger the workflow
const result = await $<SuccessResult | FailureResult | RejectionResult>({
  path: 'f/workflows/env_promoter',
  args: {
    artifactId: 'my-app',
    version: '1.2.3'
  }
});

// Handle the result
if (result.status === 'promoted') {
  console.log('Promotion successful:', result);
} else if (result.status === 'rejected') {
  console.log('Promotion rejected at staging:', result);
} else {
  console.log('Promotion failed:', result);
}
```

## Error Handling

The workflow implements comprehensive error handling:

- **Dev failures**: Immediate return with failure status
- **Staging failures**: Automatic rollback of staging environment
- **Production failures**: Automatic rollback of both production and staging environments
- **Test failures**: Automatic rollback of the affected environment(s)
- **Approval rejection**: Automatic rollback of staging environment

## Approval Process

When the workflow reaches the approval stage:

1. It generates approval URLs using `getResumeUrls()`
2. Logs the approval page URL for reference
3. Waits for human approval with a 24-hour timeout
4. If approved, proceeds to production deployment
5. If rejected or timeout, rolls back staging and returns rejection result

## Rollback Strategy

| Environment | Rollback Trigger |
|-------------|-----------------|
| Dev | No rollback (early failure) |
| Staging | On deployment failure, test failure, or approval rejection |
| Production | On deployment failure or test failure (also rolls back staging) |

## File Location

- **Main workflow**: `/home/user/windmill-project/f/workflows/env_promoter.ts`
- **Backup copy**: `/logs/artifacts/code/env_promoter.ts`