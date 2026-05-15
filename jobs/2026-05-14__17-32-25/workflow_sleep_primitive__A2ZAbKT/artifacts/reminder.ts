import { task, workflow, sleep } from 'windmill-client';

async function sendAlert(message: string) {
  console.log(`ALERT: ${message}`);
  return 'alert_sent';
}

async function sendFollowUp(message: string) {
  console.log(`FOLLOW-UP: ${message}`);
  return 'followup_sent';
}

export const main = workflow(async (message: string, delay_seconds: number) => {
  await task(sendAlert)(message);
  await sleep(delay_seconds);
  await task(sendFollowUp)(message);
  return 'done';
});
