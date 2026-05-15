import { task, workflow, parallel } from "windmill-client";

/**
 * Checks the status of a URL.
 * @param url The URL to check.
 */
async function checkUrl(url: string) {
  try {
    const response = await fetch(url);
    return {
      url,
      status: response.status,
      ok: response.ok,
    };
  } catch (error) {
    return {
      url,
      status: 0,
      ok: false,
    };
  }
}

/**
 * Summarizes the results of the URL checks.
 * @param results The array of results from checkUrl tasks.
 */
async function summarize(results: Array<{ url: string; status: number; ok: boolean }>) {
  const total = results.length;
  const successful = results.filter((r) => r.ok).length;
  const failed = results.filter((r) => !r.ok).length;

  return {
    total,
    successful,
    failed,
  };
}

/**
 * Main workflow to process a list of URLs in parallel with concurrency control.
 */
export const main = workflow(async (urls: string[]) => {
  const results = await parallel(urls, (url) => task(checkUrl)(url), {
    concurrency: 3,
  });

  return await task(summarize)(results);
});
