// Windmill workflow: Full SaaS Customer Onboarding
// Path: f/workflows/onboarding.ts

import * as wmill from "windmill-client";
import { writeFileSync } from "fs";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type Plan = "starter" | "pro" | "enterprise";

interface WorkflowInput {
  companyName: string;
  adminEmail: string;
  plan: Plan;
}

interface WorkspaceResult {
  workspaceId: string;
  companyName: string;
}

interface UserResult {
  userId: string;
  email: string;
}

interface BillingResult {
  billingId: string;
  plan: Plan;
}

interface ProvisioningResults {
  workspace: WorkspaceResult;
  user: UserResult;
  billing: BillingResult;
}

interface OnboardingReport {
  onboardingId: string;
  companyName: string;
  adminEmail: string;
  plan: Plan;
  workspaceId: string;
  userId: string;
  billingId: string;
}

interface OnboardingSummary extends OnboardingReport {
  status: "completed" | "failed" | "rejected_at_review";
  enabledIntegrations?: string[];
  welcomeEmailSent?: boolean;
}

// ---------------------------------------------------------------------------
// Helper: generate a unique onboarding ID
// ---------------------------------------------------------------------------

async function generateOnboardingId(): Promise<string> {
  // Stable, URL-safe ID: timestamp + random hex suffix
  const ts = Date.now().toString(36).toUpperCase();
  const rand = Math.random().toString(36).substring(2, 8).toUpperCase();
  return `OB-${ts}-${rand}`;
}

// ---------------------------------------------------------------------------
// Step implementations (each runs as an isolated Windmill step via step())
// ---------------------------------------------------------------------------

async function createWorkspace(
  companyName: string
): Promise<WorkspaceResult> {
  // In a real Windmill flow these would call external APIs / scripts.
  // Here we produce deterministic-but-realistic mock results.
  const slug = companyName
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
  const workspaceId = `ws-${slug}-${Date.now().toString(36)}`;
  return { workspaceId, companyName };
}

async function createAdminUser(adminEmail: string): Promise<UserResult> {
  const localPart = adminEmail.split("@")[0].replace(/[^a-z0-9]/gi, "");
  const userId = `usr-${localPart}-${Date.now().toString(36)}`;
  return { userId, email: adminEmail };
}

async function configureBilling(plan: Plan): Promise<BillingResult> {
  const billingId = `bill-${plan}-${Date.now().toString(36)}`;
  return { billingId, plan };
}

async function cleanupPartialProvisioning(onboardingId: string): Promise<void> {
  console.log(
    `[cleanup] Rolling back partial provisioning for onboarding ${onboardingId}`
  );
  // Real implementation would call de-provisioning APIs here.
}

async function configureIntegrations(
  workspaceId: string,
  plan: Plan
): Promise<string[]> {
  const integrationsByPlan: Record<Plan, string[]> = {
    starter: ["email", "webhook"],
    pro: ["email", "webhook", "slack", "zapier"],
    enterprise: ["email", "webhook", "slack", "zapier", "sso", "audit-log", "custom-api"],
  };
  const integrations = integrationsByPlan[plan];
  console.log(
    `[integrations] Configured for workspace ${workspaceId}: ${integrations.join(", ")}`
  );
  return integrations;
}

async function sendWelcomeEmail(
  adminEmail: string,
  workspaceId: string,
  plan: Plan
): Promise<{ sent: boolean }> {
  console.log(
    `[email] Sending welcome email to ${adminEmail} for workspace ${workspaceId} (${plan} plan)`
  );
  // Real implementation would call an email provider here.
  return { sent: true };
}

// ---------------------------------------------------------------------------
// Main workflow entry point
// ---------------------------------------------------------------------------

export async function main({
  companyName,
  adminEmail,
  plan,
}: WorkflowInput): Promise<OnboardingSummary> {
  // ── Step 1: Generate a unique onboarding ID ──────────────────────────────
  const onboardingId = await wmill.step(
    "generate-onboarding-id",
    async () => await generateOnboardingId()
  );

  console.log(`[onboarding] Started: ${onboardingId} | company=${companyName} | plan=${plan}`);

  // ── Step 2: Parallel provisioning ────────────────────────────────────────
  let provisioning: ProvisioningResults;

  try {
    const [workspace, user, billing] = await Promise.all([
      wmill.step(
        "provision-workspace",
        async () => await createWorkspace(companyName)
      ),
      wmill.step(
        "provision-admin-user",
        async () => await createAdminUser(adminEmail)
      ),
      wmill.step(
        "provision-billing",
        async () => await configureBilling(plan)
      ),
    ]);

    provisioning = { workspace, user, billing };
  } catch (provisioningError) {
    // ── Step 3: Cleanup on provisioning failure ───────────────────────────
    console.error(`[onboarding] Provisioning failed:`, provisioningError);

    await wmill.step(
      "cleanup-partial-provisioning",
      async () => await cleanupPartialProvisioning(onboardingId)
    );

    return {
      onboardingId,
      companyName,
      adminEmail,
      plan,
      workspaceId: "",
      userId: "",
      billingId: "",
      status: "failed",
    };
  }

  const { workspace, user, billing } = provisioning;

  // ── Step 4: Enterprise human-review gate ─────────────────────────────────
  if (plan === "enterprise") {
    const approved = await wmill.waitForApproval({
      timeout: 172800, // 48 hours in seconds
      approvalMessage: [
        `Enterprise onboarding review required.`,
        `Onboarding ID : ${onboardingId}`,
        `Company       : ${companyName}`,
        `Admin email   : ${adminEmail}`,
        `Workspace ID  : ${workspace.workspaceId}`,
        `User ID       : ${user.userId}`,
        `Billing ID    : ${billing.billingId}`,
        ``,
        `Please approve or reject this enterprise onboarding request.`,
      ].join("\n"),
    });

    if (!approved) {
      console.warn(`[onboarding] Enterprise review rejected for ${onboardingId}`);

      await wmill.step(
        "cleanup-rejected-provisioning",
        async () => await cleanupPartialProvisioning(onboardingId)
      );

      return {
        onboardingId,
        companyName,
        adminEmail,
        plan,
        workspaceId: workspace.workspaceId,
        userId: user.userId,
        billingId: billing.billingId,
        status: "rejected_at_review",
      };
    }

    console.log(`[onboarding] Enterprise review approved for ${onboardingId}`);
  }

  // ── Step 5a: Configure integrations ──────────────────────────────────────
  const enabledIntegrations = await wmill.step(
    "configure-integrations",
    async () => await configureIntegrations(workspace.workspaceId, plan)
  );

  // ── Step 5b: Send welcome email ───────────────────────────────────────────
  const emailResult = await wmill.step(
    "send-welcome-email",
    async () => await sendWelcomeEmail(adminEmail, workspace.workspaceId, plan)
  );

  // ── Step 6: Write onboarding report ──────────────────────────────────────
  const report: OnboardingReport = {
    onboardingId,
    companyName,
    adminEmail,
    plan,
    workspaceId: workspace.workspaceId,
    userId: user.userId,
    billingId: billing.billingId,
  };

  await wmill.step("write-onboarding-report", async () => {
    writeFileSync(
      "/home/user/windmill-project/onboarding_report.json",
      JSON.stringify(report, null, 2),
      "utf-8"
    );
    console.log(`[onboarding] Report written to onboarding_report.json`);
  });

  // ── Step 7: Return full onboarding summary ────────────────────────────────
  const summary: OnboardingSummary = {
    ...report,
    status: "completed",
    enabledIntegrations,
    welcomeEmailSent: emailResult.sent,
  };

  console.log(`[onboarding] Completed successfully: ${onboardingId}`);

  return summary;
}
