import { task, workflow, parallel } from 'windmill-client';

async function checkUrl(url: string): Promise<{ url: string; status: number; ok: boolean }> {
  const response = await fetch(url);
  return { url, status: response.status, ok: response.ok };
}

export const main = workflow(async (urls: string[]) => {
  const results = await parallel(
    urls.map(url => task(checkUrl)(url)),
    { concurrency: 3 }
  );
  const summary = results.filter(r => r.ok).length;
  return { results, summary };
});