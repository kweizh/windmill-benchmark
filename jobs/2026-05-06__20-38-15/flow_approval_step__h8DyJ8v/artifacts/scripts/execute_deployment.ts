export async function main(deploy_command: string, approved: boolean = true) {
  if (!approved) {
    return { status: "cancelled", message: "Deployment was not approved" };
  }
  return { status: "deployed", command_run: deploy_command, deployed_at: new Date().toISOString() };
}
