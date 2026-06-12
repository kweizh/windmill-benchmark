import { workflow, step } from "windmill-client";

export const main = workflow(
  "wac-step-determinism",
  async function (): Promise<{ timestamp: string; date: string }> {
    const timestamp = await step(
      "init_time",
      () => new Date().toISOString()
    );

    const date = timestamp.slice(0, 10);

    return { timestamp, date };
  }
);
