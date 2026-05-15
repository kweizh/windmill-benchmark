import { task, workflow } from 'windmill-client';
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
  // BUG 1: Non-deterministic - direct Date.now() in workflow body
  const startTime = Date.now();
  // BUG 2: Non-deterministic - direct randomUUID() in workflow body
  const orderId = randomUUID();
  // BUG 3: Non-deterministic - Math.random() in workflow body
  const discount = Math.random() * 0.1;
  // BUG 4: Non-deterministic - env var read in workflow body  
  const taxRate = parseFloat(process.env.TAX_RATE || '0.1');
  
  const result = await task(processOrder)(orderId, items, taxRate, discount);
  await task(sendConfirmation)(orderId, result.total);
  return { ...result, startTime };
});