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
  // Fixed: Non-deterministic calls wrapped with step()
  const startTime = await step(() => Date.now());
  const orderId = await step(() => randomUUID());
  const discount = await step(() => Math.random() * 0.1);
  const taxRate = await step(() => parseFloat(process.env.TAX_RATE || '0.1'));
  
  const result = await task(processOrder)(orderId, items, taxRate, discount);
  await task(sendConfirmation)(orderId, result.total);
  return { ...result, startTime };
});