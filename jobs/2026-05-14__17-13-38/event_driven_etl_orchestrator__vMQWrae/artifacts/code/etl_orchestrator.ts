import * as wmill from "windmill-client";
import * as fs from "fs/promises";

type Event = {
  id: string;
  type: string;
  payload: any;
};

// Mock task for enriching an event
async function enrichEvent(event: Event) {
  // Simulate some async enrichment work
  await new Promise(resolve => setTimeout(resolve, 50));
  return { ...event, enriched: true, processedAt: new Date().toISOString() };
}

export async function main(
  events: Event[],
  warehouseTarget: string = 'main'
) {
  const stateFile = '/home/user/windmill-project/processed_events.json';
  
  // 2. Read previously processed event IDs
  let processedIds: string[] = [];
  try {
    const data = await fs.readFile(stateFile, 'utf-8');
    processedIds = JSON.parse(data);
  } catch (e) {
    processedIds = [];
  }
  
  const processedSet = new Set(processedIds);
  
  // Filter out duplicates
  const newEvents = events.filter(e => !processedSet.has(e.id));
  
  if (newEvents.length === 0) {
    return { 
      status: 'success', 
      summary: 'No new events to process. All provided events were duplicates.' 
    };
  }

  // 3. Enrich new events in parallel (max 5 concurrent)
  const enrichedEvents: any[] = [];
  const inFlight = new Set<Promise<void>>();
  
  for (const event of newEvents) {
    const p = enrichEvent(event).then(res => {
      enrichedEvents.push(res);
    });
    
    inFlight.add(p);
    p.finally(() => inFlight.delete(p));
    
    if (inFlight.size >= 5) {
      await Promise.race(inFlight);
    }
  }
  await Promise.all(inFlight);

  // 4. Obtain resume/approval URLs
  const approvalUrls = await wmill.getResumeUrls('approver');
  console.log('Approval required. Please visit:', approvalUrls.approvalPage);

  // 5. Wait for human approval
  // Assuming wmill.waitForApproval suspends the workflow until approval/rejection
  const approvalResult = await wmill.waitForApproval({ timeout: 86400 });

  // 7. On rejection, return rejection summary
  if (!approvalResult || approvalResult.approved === false) {
    return {
      status: 'rejected',
      summary: 'Human approval was rejected or timed out. No data was written to the warehouse.'
    };
  }

  // 6. On approval, write to warehouse and update state
  console.log(`Writing ${enrichedEvents.length} events to warehouse target: ${warehouseTarget}`);
  // (Mock warehouse write)

  // Update processed_events.json with newly processed IDs
  const newIds = newEvents.map(e => e.id);
  const updatedIds = [...processedIds, ...newIds];
  
  await fs.writeFile(stateFile, JSON.stringify(updatedIds, null, 2), 'utf-8');

  return {
    status: 'success',
    summary: `Successfully enriched, approved, and wrote ${newEvents.length} events to ${warehouseTarget}.`,
    writtenIds: newIds
  };
}
