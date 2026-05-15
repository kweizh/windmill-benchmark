import { workflow, step, task, parallel } from 'windmill-client';

function chunkArray<T>(arr: T[], size: number): T[][] {
  const chunks: T[][] = [];
  for (let i = 0; i < arr.length; i += size) {
    chunks.push(arr.slice(i, i + size));
  }
  return chunks;
}

async function enrichUser(userId: number) {
  return { userId, name: 'User ' + userId, score: userId * 7, enriched: true };
}

async function aggregateResults(batches: any[][]) {
  const flatResults = batches.flat();
  return { total: flatResults.length, batches: batches.length, results: flatResults };
}

export default workflow(async (userIds: number[], batchSize: number = 5) => {
  const runId = await step(async () => `run-${Date.now()}`);

  const allBatchResults: any[][] = [];
  const batches = chunkArray(userIds, batchSize);

  for (const batch of batches) {
    const batchResult = await parallel(
      batch,
      (id) => task(enrichUser, { concurrency_limit: 10, concurrency_key: 'user-enrichment' })(id)
    );
    allBatchResults.push(batchResult);
  }

  const result = await task(aggregateResults)(allBatchResults);
  return result;
});
