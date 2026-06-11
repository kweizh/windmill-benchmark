import * as wmill from "windmill-client";

export async function main(): Promise<{ previous: string; next: string }> {
  const path = "f/eval/session_token";

  const previous = await wmill.getVariable(path);
  const next = previous + "_rotated";

  await wmill.setVariable(path, next);

  return { previous, next };
}
