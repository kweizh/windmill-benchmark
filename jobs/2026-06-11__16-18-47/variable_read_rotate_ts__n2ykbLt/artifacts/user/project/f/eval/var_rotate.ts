import * as wmill from "windmill-client";

export async function main(): Promise<{ previous: string; next: string }> {
  const currentValue: string = await wmill.getVariable("f/eval/session_token");
  const rotatedValue: string = currentValue + "_rotated";
  await wmill.setVariable("f/eval/session_token", rotatedValue);
  return { previous: currentValue, next: rotatedValue };
}