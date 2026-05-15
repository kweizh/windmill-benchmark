import { task, workflow } from 'windmill-client';

export const main = workflow(async (url: string) => {
  const rawData = await task('__mod/fetchData')(url);
  const processed = await task('__mod/processRecords')(rawData);
  return await task('__mod/saveReport')(processed);
});