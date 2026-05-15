import { task, workflow, parallel } from 'windmill-client';

async function checkUrl(url: string): Promise<{ url: string; status: number; ok: boolean }> {
  try {
    const response = await fetch(url);
    return {
      url,
      status: response.status,
      ok: response.ok
    };
  } catch (error) {
    return {
      url,
      status: 0,
      ok: false
    };
  }
}

async function summarize(results: Array<{ url: string; status: number; ok: boolean }>): Promise<{
  total: number;
  successful: number;
  failed: number;
}> {
  const successful = results.filter((r) => r.ok === true).length;
  const failed = results.filter((r) => r.ok === false).length;
  return {
    total: results.length,
    successful,
    failed
  };
}

export const main = workflow(async (urls: string[]) => {
  const results = await parallel(urls, (url) => task(checkUrl)(url), { concurrency: 3 });
  const summary = await task(summarize)(results);
  return summary;
});