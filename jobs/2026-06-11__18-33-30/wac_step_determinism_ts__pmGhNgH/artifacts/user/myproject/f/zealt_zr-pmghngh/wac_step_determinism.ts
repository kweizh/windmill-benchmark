import { step, workflow } from "windmill-client";

export const main = workflow(async () => {
  const timestamp = await step("init_time", () => new Date().toISOString());
  const date_portion = timestamp.substring(0, 10);

  return {
    captured_timestamp: timestamp,
    derived_date: date_portion,
  };
});