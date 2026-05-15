import { task, workflow } from 'windmill-client';

async function fetchData(url: string) {
  const resp = await fetch(url);
  return resp.json();
}

async function processRecords(data: any[]) {
  return data.map(item => ({ ...item, processed: true, count: data.length }));
}

async function saveReport(results: any[]) {
  console.log(`Report: ${results.length} records processed`);
  return { total: results.length, status: 'saved' };
}

export const main = workflow(async (url: string) => {
  const rawData = await task(fetchData)(url);
  const processed = await task(processRecords)(rawData);
  return await task(saveReport)(processed);
});