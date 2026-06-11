import * as wmill from "windmill-client";

export async function main() {
  const previous = await wmill.getVariable("f/eval/session_token");
  const next = previous + "_rotated";
  await wmill.setVariable("f/eval/session_token", next);
  return { previous, next };
}
