// Windmill workflow for complete SaaS customer onboarding
// This workflow orchestrates the entire onboarding process with proper error handling
// and human review for enterprise plans.

import { step, waitForApproval, fs } from '@windmill-labs/windmill-ts-sdk';

// Mock task functions (in real implementation, these would be actual Windmill scripts)
async function createWorkspace(companyName: string) {
  // Simulate workspace creation
  const workspaceId = `workspace_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  return { workspaceId, companyName };
}

async function createAdminUser(adminEmail: string) {
  // Simulate user creation
  const userId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  return { userId, email: adminEmail };
}

async function configureBilling(plan: 'starter' | 'pro' | 'enterprise') {
  // Simulate billing configuration
  const billingId = `billing_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  return { billingId, plan };
}

async function cleanupPartialProvisioning(onboardingId: string) {
  // Simulate cleanup of partially provisioned resources
  console.log(`Cleaning up partial provisioning for onboardingId: ${onboardingId}`);
  return { cleaned: true };
}

async function configureIntegrations(workspaceId: string, plan: 'starter' | 'pro' | 'enterprise') {
  // Simulate integration configuration based on plan
  const integrationsByPlan = {
    starter: ['email', 'basic_analytics'],
    pro: ['email', 'basic_analytics', 'advanced_analytics', 'api_access'],
    enterprise: ['email', 'basic_analytics', 'advanced_analytics', 'api_access', 'sso', 'custom_integrations', 'webhooks']
  };
  
  const enabledIntegrations = integrationsByPlan[plan] || [];
  console.log(`Configured integrations for workspace ${workspaceId}:`, enabledIntegrations);
  return enabledIntegrations;
}

async function sendWelcomeEmail(adminEmail: string, workspaceId: string, plan: 'starter' | 'pro' | 'enterprise') {
  // Simulate sending welcome email
  console.log(`Sending welcome email to ${adminEmail} for workspace ${workspaceId} on ${plan} plan`);
  return { sent: true };
}

// Main workflow function
export async function main(
  companyName: string,
  adminEmail: string,
  plan: 'starter' | 'pro' | 'enterprise'
) {
  
  // Step 1: Generate unique onboardingId
  const onboardingId = await step(async () => {
    return `onboarding_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }, { id: 'generate_onboarding_id' });
  
  console.log(`Starting onboarding with ID: ${onboardingId}`);
  
  // Step 2: Provision resources in parallel using Promise.all()
  let provisioningResults;
  try {
    provisioningResults = await step(async () => {
      const results = await Promise.all([
        createWorkspace(companyName),
        createAdminUser(adminEmail),
        configureBilling(plan)
      ]);
      
      return {
        workspace: results[0],
        user: results[1],
        billing: results[2]
      };
    }, { id: 'provision_resources' });
    
    console.log('Provisioning completed successfully:', provisioningResults);
  } catch (error) {
    // Step 3: Handle provisioning failure
    console.error('Provisioning failed:', error);
    const cleanupResult = await step(async () => {
      return cleanupPartialProvisioning(onboardingId);
    }, { id: 'cleanup_after_provisioning_failure' });
    
    return {
      onboardingId,
      status: 'failed',
      error: error instanceof Error ? error.message : 'Unknown provisioning error',
      cleanupCompleted: cleanupResult.cleaned
    };
  }
  
  const { workspace, user, billing } = provisioningResults;
  
  // Step 4: Enterprise plan requires human review
  if (plan === 'enterprise') {
    const approvalResult = await step(async () => {
      return waitForApproval({
        timeout: 172800, // 48 hours in seconds
        message: `Enterprise plan onboarding for ${companyName} requires review. Workspace: ${workspace.workspaceId}, Admin: ${adminEmail}`
      });
    }, { id: 'enterprise_review' });
    
    if (!approvalResult.approved) {
      console.log('Enterprise onboarding rejected at review stage');
      
      // Cleanup and return rejection status
      await step(async () => {
        return cleanupPartialProvisioning(onboardingId);
      }, { id: 'cleanup_after_rejection' });
      
      return {
        onboardingId,
        status: 'rejected_at_review',
        companyName,
        adminEmail,
        plan,
        rejectionReason: approvalResult.reason || 'No reason provided'
      };
    }
    
    console.log('Enterprise onboarding approved');
  }
  
  // Step 5: Run post-provisioning setup tasks sequentially
  const integrations = await step(async () => {
    return configureIntegrations(workspace.workspaceId, plan);
  }, { id: 'configure_integrations' });
  
  console.log('Configured integrations:', integrations);
  
  const emailResult = await step(async () => {
    return sendWelcomeEmail(adminEmail, workspace.workspaceId, plan);
  }, { id: 'send_welcome_email' });
  
  console.log('Welcome email sent:', emailResult);
  
  // Step 6: Write onboarding report
  await step(async () => {
    const reportData = {
      onboardingId,
      companyName,
      adminEmail,
      plan,
      workspaceId: workspace.workspaceId,
      userId: user.userId,
      billingId: billing.billingId,
      status: 'completed',
      completedAt: new Date().toISOString(),
      configuredIntegrations: integrations
    };
    
    // Write report to file system
    const reportPath = '/home/user/windmill-project/onboarding_report.json';
    await fs.writeTextFile(reportPath, JSON.stringify(reportData, null, 2));
    
    console.log(`Onboarding report written to ${reportPath}`);
    return reportData;
  }, { id: 'write_onboarding_report' });
  
  // Step 7: Return full onboarding summary
  const summary = {
    onboardingId,
    companyName,
    adminEmail,
    plan,
    workspaceId: workspace.workspaceId,
    userId: user.userId,
    billingId: billing.billingId,
    status: 'completed',
    integrations,
    welcomeEmailSent: emailResult.sent
  };
  
  console.log('Onboarding completed successfully:', summary);
  return summary;
}