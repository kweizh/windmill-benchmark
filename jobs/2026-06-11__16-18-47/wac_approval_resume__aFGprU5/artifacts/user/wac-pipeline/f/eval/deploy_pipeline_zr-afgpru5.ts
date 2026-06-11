import {
  workflow,
  step,
  waitForApproval,
  getVariable,
  setVariable,
} from "windmill-client";

export const main = workflow(async () => {
  const audit: string[] = [];

  // Step 1: Run tests
  const testResult = await step("runTests", async () => {
    // Atomically increment the counter variable
    let prevCount = 0;
    try {
      const val = await getVariable("f/eval/runtests_counter_zr-afgpru5");
      prevCount = parseInt(val as string, 10);
      if (isNaN(prevCount)) {
        prevCount = 0;
      }
    } catch {
      prevCount = 0;
    }
    await setVariable("f/eval/runtests_counter_zr-afgpru5", String(prevCount + 1));
    return "tests-ran";
  });
  audit.push(testResult);

  // Step 2: Deploy staging
  const stagingResult = await step("deployStaging", async () => {
    return "staging-deployed";
  });
  audit.push(stagingResult);

  // Step 3: Wait for external approval (suspend)
  await waitForApproval({ timeout: 600 });

  // Step 4: Deploy production
  const prodResult = await step("deployProduction", async () => {
    return "production-deployed";
  });
  audit.push(prodResult);

  return audit;
});