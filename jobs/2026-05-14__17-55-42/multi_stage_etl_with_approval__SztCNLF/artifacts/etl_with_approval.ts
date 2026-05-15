import {
  step,
  parallel,
  task,
  getResumeUrls,
  waitForApproval,
  workflow,
} from 'windmill-client';

// Fetches JSON from a single endpoint; returns an error sentinel on failure
async function extractEndpoint(endpoint: string) {
  try {
    const resp = await fetch(endpoint);
    const data = await resp.json();
    return { endpoint, data };
  } catch (_err) {
    return { endpoint, data: [], error: true };
  }
}

// Stamps each record with a transformed flag and propagates the runId
async function transformRecord(record: any) {
  return { ...record, transformed: true, runId: record.runId || 'unknown' };
}

// Simulates a data load; returns a count and completion status
async function loadData(records: any[], runId: string) {
  console.log(`Loading ${records.length} records for run ${runId}`);
  return { loaded: records.length, runId, status: 'complete' };
}

export async function main(endpoints: string[]) {
  // 1. Deterministic run ID
  const runId = await step('run_id', () => crypto.randomUUID());

  // 2. Parallel extraction (concurrency: 5)
  const extractResults = await parallel(
    endpoints.map((ep) => task(extractEndpoint)(ep)),
    { concurrency: 5 }
  );

  // 3. Parallel transformation (concurrency: 10)
  const allRecords = extractResults.flatMap((r: any) => r.data ?? []);
  const transformedRecords = await parallel(
    allRecords.map((rec: any) => task(transformRecord)(rec)),
    { concurrency: 10 }
  );

  // 4. Generate and log the approval URL inside a step
  await step('approval_urls', async () => {
    const resumeUrls = await getResumeUrls();
    console.log('Approval URL:', resumeUrls.approveUrl);
    return resumeUrls;
  });

  // 5. Suspend until a human approves or rejects
  const approval = await waitForApproval({ timeout: 3600 });

  // 6. Rejection branch
  if (!approval.approved) {
    return { runId, status: 'rejected', approver: approval.approver };
  }

  // 7. Approval branch — load and report
  const loadResult = await task(loadData)(transformedRecords, runId);
  return { runId, status: 'loaded', count: loadResult.loaded, approver: approval.approver };
}

export default workflow(main);