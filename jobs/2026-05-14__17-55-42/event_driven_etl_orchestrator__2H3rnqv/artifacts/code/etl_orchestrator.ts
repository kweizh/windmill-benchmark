import * as wmill from "windmill";

interface Event {
  id: string;
  type: string;
  payload: any;
}

interface EnrichedEvent extends Event {
  enrichedAt: string;
  enrichedData?: any;
}

interface ApprovalResult {
  approved: boolean;
  comment?: string;
}

interface SuccessSummary {
  status: "approved";
  warehouseTarget: string;
  totalEvents: number;
  newEventsProcessed: number;
  duplicateEventsSkipped: number;
  processedEventIds: string[];
  enrichedEvents: EnrichedEvent[];
  approvalComment?: string;
}

interface RejectionSummary {
  status: "rejected";
  warehouseTarget: string;
  totalEvents: number;
  newEventsPending: number;
  duplicateEventsSkipped: number;
  pendingEventIds: string[];
  rejectionComment?: string;
}

type WorkflowResult = SuccessSummary | RejectionSummary;

export async function main(
  events: Event[],
  warehouseTarget: string = "main"
): Promise<WorkflowResult> {
  // Step 1: Read previously processed event IDs
  const processedIdsPath = "/home/user/windmill-project/processed_events.json";
  let processedIds: string[] = [];
  
  try {
    const processedIdsContent = await wmill.fs.read(processedIdsPath);
    processedIds = JSON.parse(processedIdsContent);
  } catch (error) {
    // File doesn't exist or is invalid, start with empty array
    processedIds = [];
  }

  // Step 2: Deduplicate events
  const processedIdsSet = new Set(processedIds);
  const newEvents = events.filter(event => !processedIdsSet.has(event.id));
  const duplicateEvents = events.filter(event => processedIdsSet.has(event.id));

  console.log(`Total events: ${events.length}`);
  console.log(`New events to process: ${newEvents.length}`);
  console.log(`Duplicate events skipped: ${duplicateEvents.length}`);

  if (newEvents.length === 0) {
    console.log("No new events to process");
    return {
      status: "approved",
      warehouseTarget,
      totalEvents: events.length,
      newEventsProcessed: 0,
      duplicateEventsSkipped: duplicateEvents.length,
      processedEventIds: [],
      enrichedEvents: []
    };
  }

  // Step 3: Enrich new events in parallel (max 5 concurrent)
  console.log("Enriching new events...");
  const enrichedEvents = await processEventsWithConcurrency(newEvents, 5);

  // Step 4: Get approval URL before requesting human approval
  const approvalInfo = await wmill.getResumeInfo();
  const approvalUrl = approvalInfo.resume_url;
  
  console.log("=== APPROVAL REQUIRED ===");
  console.log(`Approval URL: ${approvalUrl}`);
  console.log(`Events awaiting approval: ${enrichedEvents.length}`);
  console.log(`Event IDs: ${enrichedEvents.map(e => e.id).join(", ")}`);
  console.log("========================");

  // Step 5: Wait for human approval
  const approvalResult = await waitForApproval(enrichedEvents);

  // Step 6: Handle approval or rejection
  if (approvalResult.approved) {
    // On approval: write to warehouse, update processed_events.json, return success summary
    await writeToWarehouse(enrichedEvents, warehouseTarget);
    await updateProcessedEvents(processedIds, enrichedEvents.map(e => e.id));
    
    return {
      status: "approved",
      warehouseTarget,
      totalEvents: events.length,
      newEventsProcessed: enrichedEvents.length,
      duplicateEventsSkipped: duplicateEvents.length,
      processedEventIds: enrichedEvents.map(e => e.id),
      enrichedEvents,
      approvalComment: approvalResult.comment
    };
  } else {
    // On rejection: return rejection summary without writing
    return {
      status: "rejected",
      warehouseTarget,
      totalEvents: events.length,
      newEventsPending: enrichedEvents.length,
      duplicateEventsSkipped: duplicateEvents.length,
      pendingEventIds: enrichedEvents.map(e => e.id),
      rejectionComment: approvalResult.comment
    };
  }
}

async function processEventsWithConcurrency(
  events: Event[],
  maxConcurrency: number
): Promise<EnrichedEvent[]> {
  const results: EnrichedEvent[] = [];
  
  for (let i = 0; i < events.length; i += maxConcurrency) {
    const batch = events.slice(i, i + maxConcurrency);
    const batchPromises = batch.map(event => enrichEvent(event));
    const batchResults = await Promise.all(batchPromises);
    results.push(...batchResults);
  }
  
  return results;
}

async function enrichEvent(event: Event): Promise<EnrichedEvent> {
  // This is a placeholder for the actual enrichment logic
  // In a real scenario, this would call a Windmill task/flow to enrich the event
  console.log(`Enriching event ${event.id} of type ${event.type}`);
  
  // Simulate enrichment by adding timestamp and some enriched data
  const enrichedEvent: EnrichedEvent = {
    ...event,
    enrichedAt: new Date().toISOString(),
    enrichedData: {
      enriched: true,
      processingTimestamp: new Date().toISOString(),
      eventTypeCategory: event.type.split("_")[0] || "unknown"
    }
  };
  
  return enrichedEvent;
}

async function waitForApproval(events: EnrichedEvent[]): Promise<ApprovalResult> {
  // Use Windmill's approval mechanism
  const approvalData = {
    title: `ETL Orchestrator Approval Request`,
    description: `Please approve the processing of ${events.length} events for the data warehouse.`,
    events: events.map(e => ({
      id: e.id,
      type: e.type,
      enrichedAt: e.enrichedAt
    }))
  };
  
  // This will pause the workflow and wait for human approval via the Windmill UI
  const approval = await wmill.approval.create(
    approvalData.title,
    approvalData.description,
    approvalData
  );
  
  return {
    approved: approval.approved,
    comment: approval.comment
  };
}

async function writeToWarehouse(events: EnrichedEvent[], target: string): Promise<void> {
  console.log(`Writing ${events.length} events to warehouse target: ${target}`);
  
  // This is a placeholder for the actual warehouse write logic
  // In a real scenario, this would write to Snowflake, BigQuery, PostgreSQL, etc.
  for (const event of events) {
    console.log(`  - Writing event ${event.id} to ${target}`);
    // Simulate warehouse write operation
    await new Promise(resolve => setTimeout(resolve, 10));
  }
  
  console.log("Successfully wrote all events to warehouse");
}

async function updateProcessedEvents(
  existingIds: string[],
  newIds: string[]
): Promise<void> {
  const processedIdsPath = "/home/user/windmill-project/processed_events.json";
  const updatedIds = [...existingIds, ...newIds];
  
  await wmill.fs.write(
    processedIdsPath,
    JSON.stringify(updatedIds, null, 2)
  );
  
  console.log(`Updated processed_events.json with ${newIds.length} new event IDs`);
}