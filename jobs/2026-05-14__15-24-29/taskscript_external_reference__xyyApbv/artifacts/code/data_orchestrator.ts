import { task, taskScript, workflow } from 'windmill-client';

async function saveResults(results: any[]) {
  console.log(`Saving ${results.length} results`);
  return { saved: results.length, status: 'success' };
}

export const main = workflow(async (limit: number) => {
  const users = await taskScript('f/data/extract_users')({ limit });
  const transformed = await taskScript('f/data/transform_records')({ records: users });
  return await task(saveResults)(transformed);
});
