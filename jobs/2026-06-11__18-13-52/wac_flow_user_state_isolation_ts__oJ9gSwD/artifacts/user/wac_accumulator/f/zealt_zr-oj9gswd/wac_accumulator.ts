import { getFlowUserState, setFlowUserState, step } from "windmill-client";

export async function main(values: number[]) {
  await step("init", async () => {
    await setFlowUserState({ acc: 0 });
  });

  for (let i = 0; i < values.length; i++) {
    await step(`add_${i}`, async () => {
      const state = await getFlowUserState();
      const current = (state.acc as number) || 0;
      await setFlowUserState({ acc: current + values[i] });
    });
  }

  const finalState = await step("final", async () => {
    return await getFlowUserState();
  });

  return { accumulator: finalState.acc as number };
}
