import { task, workflow } from 'windmill-client';

async function fetchData(source: string) {
  const resp = await fetch(`https://api.example.com/data?source=${source}`);
  if (!resp.ok) throw new Error(`HTTP ${resp.status}: failed to fetch ${source}`);
  return resp.json();
}

async function fallbackData(source: string) {
  console.log(`Using fallback data for source: ${source}`);
  return { source, items: [], fallback: true };
}

async function transform(data: any) {
  const items = data.items || [];
  return { count: items.length, processed: true, source: data.source };
}

export const main = workflow(async (source: string) => {
  // BUG: No error handling - if fetchData fails, the whole workflow crashes
  const data = await task(fetchData)(source);
  const result = await task(transform)(data);
  return result;
});
