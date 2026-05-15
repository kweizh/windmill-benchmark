import { task, workflow, sleep } from 'windmill-client';

async function callApi(payload: object) {
  const res = await fetch('https://api.example.com/submit', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export const main = workflow(async (payload: object, maxRetries: number = 3) => {
  let lastError: unknown;
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const result = await task(callApi)(payload);
      return result;
    } catch (e) {
      lastError = e;
      if (attempt < maxRetries) {
        await sleep(5 * Math.pow(2, attempt - 1));
      }
    }
  }
  throw lastError;
});