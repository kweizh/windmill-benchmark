import * as wmill from "windmill-client";

export async function main() {
  const variablePath = "f/eval/session_token";
  
  // Read current value
  const previous = await wmill.getVariable(variablePath);
  
  // Compute rotated value
  const next = previous + "_rotated";
  
  // Write rotated value back
  await wmill.setVariable(variablePath, next);
  
  // Return result
  return { previous, next };
}
