import { task, workflow, step } from 'windmill-client';

async function processOrder(orderId: string, timestamp: number, product: string) {
  console.log(`Processing order ${orderId} for ${product} at ${timestamp}`);
  return { orderId, product, status: 'processed' };
}

async function notifyShipping(orderId: string, product: string) {
  console.log(`Shipping notification sent for order ${orderId}: ${product}`);
  return 'notification_sent';
}

export const main = workflow(async (product: string) => {
  const timestamp = await step('timestamp', () => Date.now());
  const orderId = await step('order_id', () => Math.random().toString(36).slice(2));
  
  const result = await task(processOrder)(orderId, timestamp, product);
  await task(notifyShipping)(orderId, product);
  return result;
});
