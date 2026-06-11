import { getVariable, setVariable } from "windmill-client";

export async function main() {
  const previous = await getVariable("f/eval/session_token");
  const next = previous + "_rotated";
  await setVariable("f/eval/session_token", next);
  return { previous, next };
}
