import { workflow, step, waitForApproval } from "windmill-client";
import { getVariable, setVariable } from "windmill-client";

export async function main() {
  const audit: string[] = [];

  return await workflow({}, async () => {
    // Step 1: Run tests — appends "tests-ran" and atomically increments counter
    await step("runTests", async () => {
      audit.push("tests-ran");

      const varPath = "f/eval/runtests_counter_zr-trdfmiy";
      let currentValue = 0;
      try {
        const raw = await getVariable(varPath);
        currentValue = parseInt(raw, 10) || 0;
      } catch (_e) {
        // Variable doesn't exist yet; start from 0
      }
      await setVariable(varPath, String(currentValue + 1));
    });

    // Step 2: Deploy to staging
    await step("deployStaging", async () => {
      audit.push("staging-deployed");
    });

    // Suspend until external HTTP approval
    await waitForApproval({
      timeout: 600,
    });

    // Step 3: Deploy to production
    await step("deployProduction", async () => {
      audit.push("production-deployed");
    });

    return audit;
  });
}
