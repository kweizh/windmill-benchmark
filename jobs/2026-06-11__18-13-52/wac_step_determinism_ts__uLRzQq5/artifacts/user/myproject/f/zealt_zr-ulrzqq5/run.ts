import { main } from "./wac_step_determinism.ts";

async function run() {
    // mock step
    const result = await main();
    console.log(JSON.stringify(result));
}
run();
