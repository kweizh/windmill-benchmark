import { task, workflow } from 'windmill-client';

async function validateInput(raw: string): Promise<string> {
  if (!raw || raw.trim().length === 0) {
    throw new Error('Input must be non-empty');
  }
  return raw.trim();
}

async function transformData(input: string): Promise<object> {
  return {
    original: input,
    upper: input.toUpperCase(),
    word_count: input.split(' ').length,
  };
}

async function formatOutput(data: object): Promise<object> {
  return {
    ...data,
    processed_at: new Date().toISOString(),
    status: 'complete',
  };
}

export const main = workflow(async (raw_input: string) => {
  const validated = await task(validateInput)(raw_input);
  const transformed = await task(transformData)(validated);
  return await task(formatOutput)(transformed);
});
