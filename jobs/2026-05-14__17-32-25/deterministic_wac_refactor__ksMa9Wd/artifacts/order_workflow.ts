import { task, workflow, step } from 'windmill-client';
import { randomUUID } from 'crypto';

async function processOrder(orderId: string, items: any[], taxRate: number, discount: number) {
  const subtotal = items.reduce((sum, item) => sum + item.price, 0);
  const total = subtotal * (1 + taxRate) * (1 - discount);
  return { orderId, total, items: items.length, status: 'processed' };
}

async function sendConfirmation(orderId: string, total: number) {
  console.log(`Order ${orderId} confirmed, total: ${total}`);
  return { sent: true };
}

export const main = workflow(async (items: Array<{name: string, price: number}>) => {
  // FIX 1: Wrapped Date.now() in step() so the timestamp is recorded once and replayed deterministically
  const startTime = await step(() => Date.now());
  // FIX 2: Wrapped randomUUID() in step() so the ID is generated once and replayed deterministically
  const orderId = await step(() => randomUUID());
  // FIX 3: Wrapped Math.random() in step() so the random value is captured once and replayed deterministically
  const discount = await step(() => Math.random() * 0.1);
  // FIX 4: Wrapped process.env read in step() so the env value is captured once and replayed deterministically
  const taxRate = await step(() => parseFloat(process.env.TAX_RATE || '0.1'));

  const result = await task(processOrder)(orderId, items, taxRate, discount);
  await task(sendConfirmation)(orderId, result.total);
  return { ...result, startTime };
});
