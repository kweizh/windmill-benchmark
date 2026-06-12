import { step, workflow } from 'windmill-client';

export const main = workflow(async () => {
  const timestamp = await step('init_time', () => new Date().toISOString());
  const datePortion = timestamp.substring(0, 10);
  return {
    timestamp,
    datePortion
  };
});
