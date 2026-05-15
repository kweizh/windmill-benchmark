import * as w from "https://deno.land/x/windmill@v1/mod.ts";
import { writeFileSync } from "node:fs";

/**
 * Complete customer onboarding workflow for a SaaS product.
 * 
 * @param companyName Name of the company being onboarded
 * @param adminEmail Email address of the administrator
 * @param plan Subscription plan: 'starter', 'pro', or 'enterprise'
 */
export async function main(
  companyName: string,
  adminEmail: string,
  plan: 'starter' | 'pro' | 'enterprise'
) {
  // 1. Generate a unique onboardingId using step()
  const onboardingId = await w.step(async () => {
    return `onb_${Math.random().toString(36).substring(2, 11)}`;
  });

  let workspaceId: string | undefined;
  let userId: string | undefined;
  let billingId: string | undefined;

  try {
    // 2. In parallel, provision the following resources simultaneously (use Promise.all())
    const [workspace, user, billing] = await Promise.all([
      w.step(async () => {
        // Create a workspace
        return await createWorkspace(companyName);
      }),
      w.step(async () => {
        // Create the admin user account
        return await createAdminUser(adminEmail);
      }),
      w.step(async () => {
        // Configure billing for the plan
        return await configureBilling(plan);
      })
    ]);

    workspaceId = workspace.workspaceId;
    userId = user.userId;
    billingId = billing.billingId;

  } catch (error) {
    // 3. If provisioning any resource fails, call a cleanupPartialProvisioning(onboardingId) task and return a failure object.
    await w.step(async () => {
      await cleanupPartialProvisioning(onboardingId);
    });
    return {
      onboardingId,
      status: 'failed',
      error: error instanceof Error ? error.message : String(error)
    };
  }

  // 4. If the plan is 'enterprise', pause for human review using waitForApproval({ timeout: 172800 }) (48 hours).
  if (plan === 'enterprise') {
    try {
      // In Windmill, waitForApproval suspends the execution. 
      // We assume it resumes here on approval, or throws/returns false on rejection.
      const approved = await w.waitForApproval({ timeout: 172800 });
      
      // If the implementation returns a boolean for approval status
      if (approved === false) {
        throw new Error("Rejected by reviewer");
      }
    } catch (error) {
      // On rejection, call cleanup and return { onboardingId, status: 'rejected_at_review' }.
      await w.step(async () => {
        await cleanupPartialProvisioning(onboardingId);
      });
      return { onboardingId, status: 'rejected_at_review' };
    }
  }

  // 5. Run post-provisioning setup tasks sequentially
  // Configure integrations for the plan
  const integrations = await w.step(async () => {
    return await configureIntegrations(workspaceId!, plan);
  });

  // Send welcome email
  const emailResult = await w.step(async () => {
    return await sendWelcomeEmail(adminEmail, workspaceId!, plan);
  });

  // 6. Write an onboarding report to /home/user/windmill-project/onboarding_report.json
  const report = {
    onboardingId,
    companyName,
    adminEmail,
    plan,
    workspaceId,
    userId,
    billingId
  };

  await w.step(async () => {
    writeFileSync("/home/user/windmill-project/onboarding_report.json", JSON.stringify(report, null, 2));
  });

  // 7. Return the full onboarding summary.
  return {
    ...report,
    integrations,
    emailResult,
    status: 'completed'
  };
}

// --- Task Implementations (Internal Helpers/Mocks) ---

async function createWorkspace(companyName: string) {
  // Mock implementation
  return { 
    workspaceId: `ws_${Math.random().toString(36).substring(2, 7)}`, 
    companyName 
  };
}

async function createAdminUser(email: string) {
  // Mock implementation
  return { 
    userId: `u_${Math.random().toString(36).substring(2, 7)}`, 
    email 
  };
}

async function configureBilling(plan: string) {
  // Mock implementation
  return { 
    billingId: `bill_${Math.random().toString(36).substring(2, 7)}`, 
    plan 
  };
}

async function cleanupPartialProvisioning(onboardingId: string) {
  // Mock implementation
  console.log(`Cleaning up partial provisioning for onboarding ID: ${onboardingId}`);
  return { cleaned: true };
}

async function configureIntegrations(workspaceId: string, plan: string) {
  // Mock implementation
  const integrations = plan === 'enterprise' 
    ? ['slack', 'github', 'sentry', 'okta', 'datadog'] 
    : ['slack', 'github'];
  return integrations;
}

async function sendWelcomeEmail(adminEmail: string, workspaceId: string, plan: string) {
  // Mock implementation
  return { sent: true };
}
