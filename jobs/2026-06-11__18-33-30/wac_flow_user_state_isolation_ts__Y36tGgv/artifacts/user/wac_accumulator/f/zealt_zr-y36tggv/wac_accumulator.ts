import {
  workflow,
  step,
  getFlowUserState,
  setFlowUserState,
} from "windmill-client";

export async function main(values: number[]) {
  return await workflow(async () => {
    // Step 1: Initialize the accumulator in per-flow user state
    await step("init", async () => {
      await setFlowUserState("acc", 0);
    });

    // Step 2: For each value, read-accumulate-write inside its own step
    for (const val of values) {
      await step(`add_${val}`, async () => {
        const current = (await getFlowUserState("acc")) as number;
        await setFlowUserState("acc", current + val);
      });
    }

    // Step 3: Read the final accumulator and return it
    const result = await step("result", async () => {
      return (await getFlowUserState("acc")) as number;
    });

    return { accumulator: result };
  });
}