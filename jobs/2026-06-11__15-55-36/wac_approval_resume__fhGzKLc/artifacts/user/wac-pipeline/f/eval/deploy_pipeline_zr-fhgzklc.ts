import * as wmill from "windmill-client";
import { workflow, step, waitForApproval } from "windmill-client";

export async function main() {
  const RUN_ID = "zr-fhgzklc";
  const counterPath = `f/eval/runtests_counter_${RUN_ID}`;

  const audit = await workflow("deploy-pipeline", async () => {
    const result: string[] = [];

    // Step 1: runTests — appends "tests-ran" and increments the counter variable
    const testsResult = await step("runTests", async () => {
      // Atomically increment the counter variable
      let current = 0;
      try {
        const val = await wmill.getVariable(counterPath);
        current = parseInt(val ?? "0", 10);
        if (isNaN(current)) current = 0;
      } catch (_) {
        current = 0;
      }
      await wmill.setVariable(counterPath, String(current + 1), false, `Run tests counter for ${RUN_ID}`);

      return "tests-ran";
    });
    result.push(testsResult);

    // Step 2: deployStaging — appends "staging-deployed"
    const stagingResult = await step("deployStaging", async () => {
      return "staging-deployed";
    });
    result.push(stagingResult);

    // Step 3: suspend and wait for external HTTP approval
    await waitForApproval({ timeoutSeconds: 600 });

    // Step 4: deployProduction — appends "production-deployed"
    const prodResult = await step("deployProduction", async () => {
      return "production-deployed";
    });
    result.push(prodResult);

    return result;
  });

  return audit;
}
