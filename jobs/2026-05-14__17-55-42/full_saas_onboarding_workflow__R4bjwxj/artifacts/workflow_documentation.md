# SaaS Customer Onboarding Workflow Documentation

## Overview
This Windmill workflow orchestrates the complete customer onboarding process for a SaaS product with proper error handling and human review for enterprise plans.

## File Location
- **Workflow File**: `/home/user/windmill-project/f/workflows/onboarding.ts`
- **Report Output**: `/home/user/windmill-project/onboarding_report.json`

## Input Parameters
- `companyName: string` - The name of the company being onboarded
- `adminEmail: string` - Email address of the admin user
- `plan: 'starter' | 'pro' | 'enterprise'` - The subscription plan selected

## Workflow Steps

### 1. Generate Onboarding ID
- Creates a unique `onboardingId` using `step()` function
- Format: `onboarding_{timestamp}_{random_string}`

### 2. Parallel Resource Provisioning
Uses `Promise.all()` to provision three resources simultaneously:
- **Workspace Creation**: Returns `{ workspaceId, companyName }`
- **Admin User Creation**: Returns `{ userId, email }`
- **Billing Configuration**: Returns `{ billingId, plan }`

### 3. Error Handling
If any provisioning task fails:
- Calls `cleanupPartialProvisioning(onboardingId)` to clean up
- Returns a failure object with error details

### 4. Enterprise Plan Review (Conditional)
For enterprise plans only:
- Pauses workflow using `waitForApproval({ timeout: 172800 })` (48 hours)
- On rejection: calls cleanup and returns `{ onboardingId, status: 'rejected_at_review' }`
- On approval: continues with post-provisioning setup

### 5. Post-Provisioning Setup (Sequential)
Runs in sequence:
- **Configure Integrations**: `configureIntegrations(workspaceId, plan)`
  - Starter: email, basic_analytics
  - Pro: email, basic_analytics, advanced_analytics, api_access
  - Enterprise: All pro integrations + sso, custom_integrations, webhooks
- **Send Welcome Email**: `sendWelcomeEmail(adminEmail, workspaceId, plan)`

### 6. Generate Onboarding Report
Writes to `/home/user/windmill-project/onboarding_report.json`:
```json
{
  "onboardingId": "onboarding_...",
  "companyName": "...",
  "adminEmail": "...",
  "plan": "...",
  "workspaceId": "workspace_...",
  "userId": "user_...",
  "billingId": "billing_...",
  "status": "completed",
  "completedAt": "ISO-8601 timestamp",
  "configuredIntegrations": [...]
}
```

### 7. Return Summary
Returns complete onboarding summary including:
- All IDs (onboarding, workspace, user, billing)
- Status
- Configured integrations
- Welcome email confirmation

## Return Object Structure

### Success
```typescript
{
  onboardingId: string,
  companyName: string,
  adminEmail: string,
  plan: 'starter' | 'pro' | 'enterprise',
  workspaceId: string,
  userId: string,
  billingId: string,
  status: 'completed',
  integrations: string[],
  welcomeEmailSent: true
}
```

### Provisioning Failure
```typescript
{
  onboardingId: string,
  status: 'failed',
  error: string,
  cleanupCompleted: true
}
```

### Enterprise Rejection
```typescript
{
  onboardingId: string,
  status: 'rejected_at_review',
  companyName: string,
  adminEmail: string,
  plan: 'enterprise',
  rejectionReason: string
}
```

## Key Features

### Parallel Execution
- Uses `Promise.all()` for efficient resource provisioning
- Reduces total onboarding time by running tasks concurrently

### Error Handling
- Comprehensive error handling at each stage
- Automatic cleanup of partial resources on failure

### Human Review (Enterprise Only)
- 48-hour timeout for enterprise plan approval
- Clean rejection workflow with resource cleanup

### Audit Trail
- Detailed onboarding report written to file system
- Includes timestamps and all relevant IDs

### Step Tracking
- Each major operation uses Windmill's `step()` function
- Enables better monitoring and debugging

## Integration Points

### Mock Functions
The workflow includes mock implementations for:
- `createWorkspace()` - Workspace creation
- `createAdminUser()` - User account creation
- `configureBilling()` - Billing setup
- `cleanupPartialProvisioning()` - Resource cleanup
- `configureIntegrations()` - Plan-based integrations
- `sendWelcomeEmail()` - Email notification

### Production Integration
In a production environment, replace these with:
- Actual Windmill scripts or external API calls
- Database operations for user/workspace creation
- Payment gateway integration for billing
- Email service integration for notifications
- Third-party service integrations

## Usage Example

```typescript
// Basic onboarding
const result = await main(
  'Acme Corporation',
  'admin@acme.com',
  'pro'
);

// Enterprise onboarding (triggers human review)
const enterpriseResult = await main(
  'Enterprise LLC',
  'ceo@enterprise.com',
  'enterprise'
);
```

## Testing Notes

- All mock functions generate unique IDs with timestamps
- Console logging provides visibility into workflow execution
- Error scenarios can be tested by throwing errors in mock functions
- Enterprise review timeout is set to 48 hours (172800 seconds)

## Dependencies

- `@windmill-labs/windmill-ts-sdk` - Windmill TypeScript SDK
  - `step()` - Workflow step execution
  - `waitForApproval()` - Human approval workflow
  - `fs` - File system operations