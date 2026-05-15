import { taskScript } from 'windmill-client';

export const main = taskScript(async (url: string) => {
  const resp = await fetch(url);
  return resp.json();
});