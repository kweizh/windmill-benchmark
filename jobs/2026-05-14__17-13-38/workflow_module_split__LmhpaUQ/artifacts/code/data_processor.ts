import { taskScript, workflow } from 'windmill-client';

export const main = workflow(async (url: string) => {
  const rawData = await taskScript('./data_processor__mod/fetchData.ts')(url);
  const processed = await taskScript('./data_processor__mod/processRecords.ts')(rawData);
  return await taskScript('./data_processor__mod/saveReport.ts')(processed);
});
