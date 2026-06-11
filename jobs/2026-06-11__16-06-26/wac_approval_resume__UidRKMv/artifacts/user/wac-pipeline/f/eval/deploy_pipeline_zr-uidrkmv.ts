import { workflow, step, waitForApproval, getVariable, setVariable } from "windmill-client";

export async function main() {
  return await workflow(async () => {
    const audit: string[] = [];

    const r1 = await step("runTests", async () => {
      const varPath = "f/eval/runtests_counter_zr-uidrkmv";
      let count = 0;
      try {
        const val = await getVariable(varPath);
        if (val) {
          count = parseInt(val, 10);
        }
      } catch (e) {
        count = 0;
      }
      count++;
      await setVariable(varPath, count.toString());
      return "tests-ran";
    });
    audit.push(r1 as string);

    const r2 = await step("deployStaging", async () => {
      return "staging-deployed";
    });
    audit.push(r2 as string);

    await waitForApproval({
      approver: "admin",
      timeout: 600,
    });

    const r3 = await step("deployProduction", async () => {
      return "production-deployed";
    });
    audit.push(r3 as string);

    return audit;
  });
}