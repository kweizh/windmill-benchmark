import { step, waitForApproval } from "@windmill/worker";
import * as fs from "fs";

// Mock tasks for provisioning
async function createWorkspace(companyName: string) {
  return { workspaceId: "ws_" + Date.now() + "_" + Math.floor(Math.random() * 1000), companyName };
}

async function createAdminUser(adminEmail: string) {
  return { userId: "usr_" + Date.now() + "_" + Math.floor(Math.random() * 1000), email: adminEmail };
}

async function configureBilling(plan: string) {
  return { billingId: "bill_" + Date.now() + "_" + Math.floor(Math.random() * 1000), plan };
}

async function cleanupPartialProvisioning(onboardingId: string) {
  console.log(`Cleaning up provisioning for ${onboardingId}`);
  return { cleaned: true };
}

async function configureIntegrations(workspaceId: string, plan: string) {
  return plan === "enterprise" ? ["sso", "slack", "github"] : ["slack"];
}

async function sendWelcomeEmail(adminEmail: string, workspaceId: string, plan: string) {
  return { sent: true };
}

export async function main(
  companyName: string,
  adminEmail: string,
  plan: 'starter' | 'pro' | 'enterprise'
) {
  // 1. Generate a unique onboardingId
  const onboardingId = await step("generateOnboardingId", async () => {
    return "onb_" + Math.random().toString(36).slice(2);
  });

  let provisioningResults;
  try {
    // 2. In parallel, provision the resources simultaneously
    provisioningResults = await Promise.all([
      step("createWorkspace", () => createWorkspace(companyName)),
      step("createAdminUser", () => createAdminUser(adminEmail)),
      step("configureBilling", () => configureBilling(plan))
    ]);
  } catch (error) {
    // 3. If provisioning fails, call cleanup and return failure object
    await step("cleanupPartialProvisioning", () => cleanupPartialProvisioning(onboardingId));
    return { onboardingId, status: "provisioning_failed", error: String(error) };
  }

  const [workspace, user, billing] = provisioningResults;

  // 4. If the plan is 'enterprise', pause for human review
  if (plan === "enterprise") {
    let approved = true;
    try {
      const approvalResult = await waitForApproval({ timeout: 172800 });
      if (approvalResult === false || approvalResult === null) {
        approved = false;
      }
    } catch (e) {
      // If waitForApproval throws on rejection or timeout
      approved = false;
    }

    if (!approved) {
      await step("cleanupRejectedProvisioning", () => cleanupPartialProvisioning(onboardingId));
      return { onboardingId, status: 'rejected_at_review' };
    }
  }

  // 5. Run post-provisioning setup tasks sequentially
  const integrations = await step("configureIntegrations", () => configureIntegrations(workspace.workspaceId, plan));
  const welcomeEmail = await step("sendWelcomeEmail", () => sendWelcomeEmail(adminEmail, workspace.workspaceId, plan));

  // 6. Write an onboarding report
  const report = {
    onboardingId,
    companyName,
    adminEmail,
    plan,
    workspaceId: workspace.workspaceId,
    userId: user.userId,
    billingId: billing.billingId
  };

  fs.writeFileSync("/home/user/windmill-project/onboarding_report.json", JSON.stringify(report, null, 2));

  // 7. Return the full onboarding summary
  return {
    status: "success",
    report,
    integrations,
    welcomeEmail
  };
}
