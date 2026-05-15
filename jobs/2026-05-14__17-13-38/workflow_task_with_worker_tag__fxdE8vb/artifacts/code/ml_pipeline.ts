import { task, workflow } from 'windmill-client';

async function preprocessData(data: number[]) {
  console.log(`Preprocessing ${data.length} data points`);
  return { normalized: data.map(x => x / 100), count: data.length };
}

async function trainModel(data: { normalized: number[], count: number }) {
  console.log(`Training model on ${data.count} samples`);
  return { model_id: 'ml-model-v1', accuracy: 0.95, trained_on: data.count };
}

export const main = workflow(async (rawData: number[]) => {
  // Preprocessing can run on any worker
  const processedData = await task(preprocessData)(rawData);
  // BUG: Model training should be routed to GPU workers but has no tag
  const modelResult = await task(trainModel, { tag: 'gpu' })(processedData);
  return modelResult;
});
