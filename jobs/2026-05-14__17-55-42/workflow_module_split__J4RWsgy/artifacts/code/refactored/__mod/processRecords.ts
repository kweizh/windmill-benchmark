import { taskScript } from 'windmill-client';

export const main = taskScript(async (data: any[]) => {
  return data.map(item => ({ ...item, processed: true, count: data.length }));
});