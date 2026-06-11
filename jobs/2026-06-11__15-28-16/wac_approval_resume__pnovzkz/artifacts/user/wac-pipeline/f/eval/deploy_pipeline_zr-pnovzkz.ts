import { workflow, step, waitForApproval, getVariable, setVariable } from "windmill-client";

export const main = workflow(async () => {
  const audit: string[] = [];

  const step1Result = await step("runTests", async () => {
    let currentCount = 0;
    try {
      const val = await getVariable("f/eval/runtests_counter_zr-pnovzkz");
      if (val !== undefined && val !== null) {
        currentCount = parseInt(val, 10);
      }
    } catch (e) {
      currentCount = 0;
    }
    const newCount = currentCount + 1;
    await setVariable("f/eval/runtests_counter_zr-pnovzkz", String(newCount));
    return "tests-ran";
  });
  audit.push(step1Result);

  const step2Result = await step("deployStaging", async () => {
    return "staging-deployed";
  });
  audit.push(step2Result);

  // Generous timeout (at least 600 seconds)
  await waitForApproval({ timeout: 1200 });

  const step3Result = await step("deployProduction", async () => {
    return "production-deployed";
  });
  audit.push(step3Result);

  return audit;
});
