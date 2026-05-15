import { workflow, taskScript, task } from 'windmill-client';

export const main = workflow(async (url: string) => {
  const rawData = await task(taskScript("f/workflows/data_processor/__mod/fetch_data"))(url);
  const processed = await task(taskScript("f/workflows/data_processor/__mod/process_records"))(rawData);
  return await task(taskScript("f/workflows/data_processor/__mod/save_report"))(processed);
});
