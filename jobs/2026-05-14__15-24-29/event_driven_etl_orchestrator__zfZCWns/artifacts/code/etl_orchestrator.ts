import * as wmill from "https://deno.land/x/windmill@v1.432.0/mod.ts";

interface Event {
  id: string;
  type: string;
  payload: any;
}

/**
 * Event-Driven ETL Orchestrator
 * 
 * @param events Array of events to process
 * @param warehouseTarget Target warehouse name
 */
export async function main(
  events: Event[],
  warehouseTarget: string = "main"
) {
  const statePath = "/home/user/windmill-project/processed_events.json";

  // 1. Deduplicate events
  let processedIds: string[] = [];
  try {
    const stateContent = await Deno.readTextFile(statePath);
    processedIds = JSON.parse(stateContent);
  } catch (e) {
    if (!(e instanceof Deno.errors.NotFound)) {
      console.error("Error reading state file:", e);
    }
    // If file doesn't exist, we start with an empty list
    processedIds = [];
  }

  const newEvents = events.filter((e) => !processedIds.includes(e.id));

  if (newEvents.length === 0) {
    return {
      status: "success",
      message: "No new events to process",
      processedCount: 0,
      warehouse: warehouseTarget
    };
  }

  console.log(`Found ${newEvents.length} new events out of ${events.length} provided.`);

  // 2. Enrich only the new (non-duplicate) events in parallel (max 5 concurrent)
  // This represents the "Windmill task" for enrichment
  const enrichEventTask = async (event: Event) => {
    console.log(`Enriching event: ${event.id} (${event.type})`);
    // Simulate enrichment logic
    return {
      ...event,
      enriched: true,
      enrichedAt: new Date().toISOString(),
      metadata: {
        source: "etl_orchestrator",
        version: "1.0.0"
      }
    };
  };

  const enrichedEvents = await limitConcurrency(newEvents, enrichEventTask, 5);

  // 3. Obtain resume/approval URLs
  const resumeUrls = await wmill.getResumeUrls();
  console.log("----- HUMAN APPROVAL REQUIRED -----");
  console.log(`Approve URL: ${resumeUrls.approve}`);
  console.log(`Decline URL: ${resumeUrls.decline}`);
  console.log("------------------------------------");

  // 4. Wait for human approval
  // This will suspend the workflow execution until a resume signal is received
  const approval = await wmill.waitApproval();

  if (!approval) {
    console.log("Workflow rejected by human approval.");
    return {
      status: "rejected",
      message: "ETL process was rejected during human approval",
      processedCount: 0,
      warehouse: warehouseTarget
    };
  }

  // 5. On approval, write to the warehouse
  console.log(`Writing ${enrichedEvents.length} enriched events to warehouse: ${warehouseTarget}`);
  // In a real scenario, this would call a database or another API
  // For this orchestrator, we'll simulate the successful write
  
  // 6. Update the processed_events.json file with the newly processed IDs
  const updatedProcessedIds = [...new Set([...processedIds, ...newEvents.map(e => e.id)])];
  await Deno.writeTextFile(statePath, JSON.stringify(updatedProcessedIds, null, 2));

  // 7. Return a success summary
  return {
    status: "success",
    message: "ETL orchestration completed successfully",
    processedCount: enrichedEvents.length,
    warehouse: warehouseTarget,
    newProcessedIds: newEvents.map(e => e.id)
  };
}

/**
 * Helper to limit concurrency of asynchronous tasks
 */
async function limitConcurrency<T, R>(
  items: T[],
  fn: (item: T) => Promise<R>,
  limit: number
): Promise<R[]> {
  const results: R[] = new Array(items.length);
  const queue = items.map((item, index) => ({ item, index }));
  
  async function worker() {
    while (queue.length > 0) {
      const task = queue.shift();
      if (!task) break;
      results[task.index] = await fn(task.item);
    }
  }

  const workers = Array.from({ length: Math.min(limit, items.length) }, worker);
  await Promise.all(workers);
  return results;
}
