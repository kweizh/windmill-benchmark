# Test Examples for Onboarding Workflow

## Testing the Workflow

### Example 1: Starter Plan Onboarding
```typescript
import { main } from './onboarding';

const result = await main(
  'Startup Inc',
  'founder@startup.com',
  'starter'
);

console.log('Starter plan onboarding result:', result);
```

**Expected Output:**
```json
{
  "onboardingId": "onboarding_1715726809_abc123xyz",
  "companyName": "Startup Inc",
  "adminEmail": "founder@startup.com",
  "plan": "starter",
  "workspaceId": "workspace_1715726809_def456uvw",
  "userId": "user_1715726809_ghi789rst",
  "billingId": "billing_1715726809_jkl012mno",
  "status": "completed",
  "integrations": ["email", "basic_analytics"],
  "welcomeEmailSent": true
}
```

### Example 2: Pro Plan Onboarding
```typescript
const result = await main(
  'Growth Company',
  'cto@growthco.com',
  'pro'
);

console.log('Pro plan onboarding result:', result);
```

**Expected Output:**
```json
{
  "onboardingId": "onboarding_1715726810_abc456xyz",
  "companyName": "Growth Company",
  "adminEmail": "cto@growthco.com",
  "plan": "pro",
  "workspaceId": "workspace_1715726810_def789uvw",
  "userId": "user_1715726810_ghi012rst",
  "billingId": "billing_1715726810_jkl345mno",
  "status": "completed",
  "integrations": [
    "email",
    "basic_analytics",
    "advanced_analytics",
    "api_access"
  ],
  "welcomeEmailSent": true
}
```

### Example 3: Enterprise Plan Onboarding (With Approval)
```typescript
const result = await main(
  'Enterprise Corp',
  'admin@enterprisecorp.com',
  'enterprise'
);

console.log('Enterprise plan onboarding result:', result);
```

**Expected Output (After Approval):**
```json
{
  "onboardingId": "onboarding_1715726811_abc789xyz",
  "companyName": "Enterprise Corp",
  "adminEmail": "admin@enterprisecorp.com",
  "plan": "enterprise",
  "workspaceId": "workspace_1715726811_def012uvw",
  "userId": "user_1715726811_ghi345rst",
  "billingId": "billing_1715726811_jkl678mno",
  "status": "completed",
  "integrations": [
    "email",
    "basic_analytics",
    "advanced_analytics",
    "api_access",
    "sso",
    "custom_integrations",
    "webhooks"
  ],
  "welcomeEmailSent": true
}
```

### Example 4: Enterprise Plan Onboarding (Rejected)
```typescript
const result = await main(
  'Rejected Enterprise',
  'admin@rejected.com',
  'enterprise'
);

// If rejected during review
console.log('Enterprise rejection result:', result);
```

**Expected Output (After Rejection):**
```json
{
  "onboardingId": "onboarding_1715726812_abc012xyz",
  "status": "rejected_at_review",
  "companyName": "Rejected Enterprise",
  "adminEmail": "admin@rejected.com",
  "plan": "enterprise",
  "rejectionReason": "Insufficient documentation provided"
}
```

### Example 5: Provisioning Failure
```typescript
// Simulate a failure by modifying the mock function to throw an error
const result = await main(
  'Failed Company',
  'admin@failed.com',
  'pro'
);

console.log('Provisioning failure result:', result);
```

**Expected Output:**
```json
{
  "onboardingId": "onboarding_1715726813_abc345xyz",
  "status": "failed",
  "error": "Database connection timeout",
  "cleanupCompleted": true
}
```

## Onboarding Report Example

After successful onboarding, the report file at `/home/user/windmill-project/onboarding_report.json` will contain:

```json
{
  "onboardingId": "onboarding_1715726814_abc678xyz",
  "companyName": "Success Corp",
  "adminEmail": "admin@successcorp.com",
  "plan": "pro",
  "workspaceId": "workspace_1715726814_def901uvw",
  "userId": "user_1715726814_ghi234rst",
  "billingId": "billing_1715726814_jkl567mno",
  "status": "completed",
  "completedAt": "2026-05-15T01:06:54.123Z",
  "configuredIntegrations": [
    "email",
    "basic_analytics",
    "advanced_analytics",
    "api_access"
  ]
}
```

## Integration Configuration by Plan

### Starter Plan
- email
- basic_analytics

### Pro Plan
- email
- basic_analytics
- advanced_analytics
- api_access

### Enterprise Plan
- email
- basic_analytics
- advanced_analytics
- api_access
- sso
- custom_integrations
- webhooks

## Testing Checklist

- [ ] Starter plan onboarding completes successfully
- [ ] Pro plan onboarding completes successfully
- [ ] Enterprise plan onboarding with approval completes successfully
- [ ] Enterprise plan onboarding with rejection returns correct status
- [ ] Provisioning failure triggers cleanup correctly
- [ ] Onboarding report is written to correct location
- [ ] All IDs are unique across test runs
- [ ] Parallel provisioning reduces execution time
- [ ] Enterprise review timeout is set to 48 hours
- [ ] Welcome email is sent for all successful onboarding

## Manual Testing Steps

1. **Navigate to workflow directory:**
   ```bash
   cd /home/user/windmill-project/f/workflows
   ```

2. **Run starter plan test:**
   ```bash
   echo "Testing starter plan..."
   ```

3. **Check onboarding report:**
   ```bash
   cat /home/user/windmill-project/onboarding_report.json
   ```

4. **Verify parallel execution:**
   - Check console logs for simultaneous provisioning
   - Verify all three resources are created independently

5. **Test enterprise review:**
   - Run enterprise workflow
   - Wait for approval request
   - Approve or reject to test both paths

## Performance Considerations

- **Parallel Provisioning**: Should complete in ~max(provisioning_time) rather than sum(provisioning_times)
- **Enterprise Review**: Adds up to 48 hours (172800 seconds) to workflow duration
- **Sequential Post-Setup**: Integration config and email are run sequentially for reliability
- **Error Recovery**: Cleanup adds minimal overhead but ensures system consistency