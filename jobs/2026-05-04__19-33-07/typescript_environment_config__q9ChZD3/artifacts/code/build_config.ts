export async function main(
  environment: string,
  api_base_url: string,
  debug: boolean = false,
  max_retries: number = 3,
  timeout_ms: number = 5000
) {
  const validEnvironments = ["development", "staging", "production"];
  if (!validEnvironments.includes(environment)) {
    throw new Error(`Unknown environment: ${environment}`);
  }

  return {
    environment,
    api_base_url: api_base_url.replace(/\/$/, ""), // strip trailing slash
    debug: environment !== "production" && debug,
    max_retries,
    timeout_ms,
    is_production: environment === "production",
    log_level: environment === "production" ? "warn" : "debug",
  };
}
