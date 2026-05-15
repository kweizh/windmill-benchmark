import { task, workflow, parallel } from "windmill-client";

// Task: fetch a single URL and return its status information
async function checkUrl(url: string): Promise<{ url: string; status: number; ok: boolean }> {
  try {
    const response = await fetch(url);
    return { url, status: response.status, ok: response.ok };
  } catch {
    // Network error or other fetch failure
    return { url, status: 0, ok: false };
  }
}

// Task: summarize an array of URL check results
async function summarize(
  results: Array<{ url: string; status: number; ok: boolean }>
): Promise<{ total: number; successful: number; failed: number }> {
  const total = results.length;
  const successful = results.filter((r) => r.ok === true).length;
  const failed = results.filter((r) => r.ok === false).length;
  return { total, successful, failed };
}

// Main workflow: process a list of URLs with bounded concurrency, then summarize
export const main = workflow(async (urls: string[]) => {
  const results = await parallel(
    urls,
    (url) => task(checkUrl)(url),
    { concurrency: 3 }
  );

  const summary = await task(summarize)(results);
  return summary;
});
