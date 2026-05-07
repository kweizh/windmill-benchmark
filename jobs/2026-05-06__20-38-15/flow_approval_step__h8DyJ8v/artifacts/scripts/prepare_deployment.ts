export async function main(service: string, version: string, environment: string) {
  return {
    service,
    version,
    environment,
    deploy_command: `kubectl set image deployment/${service} ${service}=${service}:${version} -n ${environment}`,
    requires_approval: true
  };
}
