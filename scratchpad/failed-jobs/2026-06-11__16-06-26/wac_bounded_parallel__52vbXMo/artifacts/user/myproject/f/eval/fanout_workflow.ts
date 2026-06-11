import { workflow, task, parallel } from 'windmill-client';

export const main = workflow(async (urls: string[]) => {
  return await parallel(
    urls,
    (url: string) => {
      return task(async () => {
        const response = await fetch(url);
        return { url, status: response.status };
      })();
    },
    { concurrency: 3 }
  );
});
