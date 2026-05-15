import { task, workflow, parallel } from 'windmill-client';

async function enrichRecord(record: { id: string, name: string }) {
  // Simulates an expensive external API call
  console.log(`Enriching record: ${record.id}`);
  return { ...record, enriched: true, score: record.name.length * 10 };
}

async function saveResults(results: any[]) {
  console.log(`Saving ${results.length} enriched records`);
  return { saved: results.length };
}

export const main = workflow(async (records: Array<{ id: string, name: string }>) => {
  // BUG: No caching - same records are enriched repeatedly on every run
  const enriched = await parallel(records, (record) => task(enrichRecord, { cache_ttl: 3600 })(record));
  return await task(saveResults)(enriched);
});
