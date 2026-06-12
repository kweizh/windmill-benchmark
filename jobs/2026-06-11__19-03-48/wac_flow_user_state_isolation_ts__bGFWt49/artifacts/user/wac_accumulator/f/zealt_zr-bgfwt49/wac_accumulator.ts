import { workflow, step, getFlowUserState, setFlowUserState } from 'windmill-client';

export const main = workflow(async (values: number[]) => {
  // Step 1: Initialize the accumulator to 0 in the per-flow user state
  await step('init_acc', async () => {
    await setFlowUserState('acc', 0);
  });

  // Step 2: Iterate over each value, read-modify-write the accumulator
  for (let i = 0; i < values.length; i++) {
    const v = values[i];
    await step(`accumulate_${i}`, async () => {
      const current: number = await getFlowUserState('acc');
      const next = current + v;
      await setFlowUserState('acc', next);
    });
  }

  // Step 3: Read the final accumulator and return it
  const finalAcc: number = await step('read_final', async () => {
    return await getFlowUserState('acc');
  });

  return { accumulator: finalAcc };
});
