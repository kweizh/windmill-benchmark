import { taskScript } from 'windmill-client';

export const main = taskScript(async (results: any[]) => {
  console.log(`Report: ${results.length} records processed`);
  return { total: results.length, status: 'saved' };
});