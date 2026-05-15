import { task, workflow, parallel } from "windmill-client";

export async function checkUrl(url: string) {
  try {
    const response = await fetch(url);
    return { url, status: response.status, ok: response.ok };
  } catch (error) {
    return { url, status: 0, ok: false };
  }
}

export async function summarize(results: Array<{url: string, status: number, ok: boolean}>) {
  const successful = results.filter(r => r.ok).length;
  const failed = results.length - successful;
  return {
    total: results.length,
    successful,
    failed
  };
}

export const main = workflow(async (urls: string[]) => {
  const results = await parallel(urls, (url) => task(checkUrl)(url), { concurrency: 3 });
  return await task(summarize)(results);
});
