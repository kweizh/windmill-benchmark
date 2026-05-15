import { workflow, step, task, parallel } from 'windmill-client';

// Pure helper — not a task — splits an array into sequential chunks of a given size.
function chunkArray<T>(arr: T[], size: number): T[][] {
  const chunks: T[][] = [];
  for (let i = 0; i < arr.length; i += size) {
    chunks.push(arr.slice(i, i + size));
  }
  return chunks;
}

// Enrichment task: given a userId, returns an enriched record.
async function enrichUser(userId: number) {
  return { userId, name: 'User ' + userId, score: userId * 7, enriched: true };
}

// Aggregation task: flattens all per-batch results into a single summary object.
async function aggregateResults(batches: any[][]) {
  const flatResults = batches.flat();
  return { total: flatResults.length, batches: batches.length, results: flatResults };
}

// Main workflow entry-point exported via Windmill's `workflow()` wrapper.
export default workflow(async (userIds: number[], batchSize: number = 5) => {
  // Step 1 — Generate a unique run ID for this execution.
  const runId = await step(async () => `run-${Date.now()}`);
  console.log(`Starting batch enrichment workflow. runId=${runId}`);

  // Step 2 — Split the full list of user IDs into sequential batches.
  const batches = chunkArray(userIds, batchSize);
  console.log(`Processing ${userIds.length} user(s) in ${batches.length} batch(es) of up to ${batchSize}.`);

  // Step 3 — Iterate over batches sequentially; within each batch, enrich all
  //           items concurrently via parallel() with shared concurrency controls.
  const allBatchResults: any[][] = [];

  for (const batch of batches) {
    const batchResult = await parallel(
      batch,
      (id) =>
        task(enrichUser, {
          concurrency_limit: 10,
          concurrency_key: 'user-enrichment',
        })(id)
    );
    allBatchResults.push(batchResult);
  }

  // Step 4 — Aggregate all collected batch results into a single summary.
  const result = await task(aggregateResults)(allBatchResults);

  return result;
});
