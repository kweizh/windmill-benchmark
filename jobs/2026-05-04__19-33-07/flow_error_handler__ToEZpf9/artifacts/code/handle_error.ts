export async function main(
  error_message: string,
  flow_path: string = "unknown",
  step_id: string = "unknown"
) {
  return {
    alert: true,
    message: `Flow '${flow_path}' failed at step '${step_id}': ${error_message}`,
    timestamp: new Date().toISOString()
  };
}
