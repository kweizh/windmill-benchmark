import { workflow, step, task, parallel } from 'windmill-client';

export async function workflow(userIds: number[], batchSize: number = 5) {
  // Step 1 — Generate a Run ID
  const runId = await step(async () => `run-${Date.now()}`);

  // Step 2 — Batch Splitting (pure helper function)
  function chunkArray<T>(arr: T[], size: number): T[][] {
    const chunks: T[][] = [];
    for (let i = 0; i < arr.length; i += size) {
      chunks.push(arr.slice(i, i + size));
    }
    return chunks;
  }

  // Step 4 — Enrichment Task
  async function enrichUser(userId: number) {
    return { userId, name: 'User ' + userId, score: userId * 7, enriched: true };
  }

  // Step 5 — Aggregation Task
  async function aggregateResults(batches: any[][]) {
    const flatResults = batches.flat();
    return { total: flatResults.length, batches: batches.length, results: flatResults };
  }

  // Step 3 — Sequential Batch Loop with Internal Parallelism
  const allBatchResults: any[][] = [];
  const batches = chunkArray(userIds, batchSize);

  for (const batch of batches) {
    const batchResult = await parallel(
      batch,
      (id) => task(enrichUser, { concurrency_limit: 10, concurrency_key: 'user-enrichment' })(id)
    );
    allBatchResults.push(batchResult);
  }

  // Step 6 — Final Aggregation
  const result = await task(aggregateResults)(allBatchResults);
  return result;
}