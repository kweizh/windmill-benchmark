import {
  task,
  step,
  workflow,
  parallel,
  waitForApproval,
  getResumeUrls,
} from "windmill-client";
import * as fs from "fs";

// ─── Types ────────────────────────────────────────────────────────────────────

interface Event {
  id: string;
  type: string;
  payload: any;
}

interface EnrichedEvent extends Event {
  enrichedAt: string;
  enrichmentMeta: {
    source: string;
    version: string;
    processingMs: number;
  };
}

interface WarehouseWriteResult {
  target: string;
  recordsWritten: number;
  writtenAt: string;
  eventIds: string[];
}

// ─── State helpers (run inline via step() for replay-safety) ──────────────────

const STATE_FILE = "/home/user/windmill-project/processed_events.json";

function readProcessedIds(): string[] {
  try {
    const raw = fs.readFileSync(STATE_FILE, "utf-8");
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function writeProcessedIds(ids: string[]): void {
  fs.writeFileSync(STATE_FILE, JSON.stringify(ids, null, 2), "utf-8");
}

// ─── Task functions (each runs as a separate Windmill child job) ──────────────

async function enrichEvent(event: Event): Promise<EnrichedEvent> {
  const start = Date.now();

  // Simulate enrichment: augment the event payload with metadata.
  // In production this would call an external API, feature store, ML model, etc.
  const enriched: EnrichedEvent = {
    ...event,
    payload: {
      ...event.payload,
      _enriched: true,
      _tags: [`type:${event.type}`, `id:${event.id}`],
    },
    enrichedAt: new Date().toISOString(),
    enrichmentMeta: {
      source: "etl-enrichment-service",
      version: "1.0.0",
      processingMs: Date.now() - start,
    },
  };

  console.log(
    `[enrichEvent] Enriched event id=${event.id} type=${event.type}`
  );
  return enriched;
}

async function writeToWarehouse(
  enrichedEvents: EnrichedEvent[],
  target: string
): Promise<WarehouseWriteResult> {
  // Simulate a warehouse write (Snowflake, BigQuery, Redshift, etc.).
  // In production this would use an SDK / REST call to your data warehouse.
  const writtenAt = new Date().toISOString();
  const eventIds = enrichedEvents.map((e) => e.id);

  console.log(
    `[writeToWarehouse] Writing ${enrichedEvents.length} records to warehouse="${target}"`
  );
  console.log(`[writeToWarehouse] Event IDs: ${eventIds.join(", ")}`);

  // Simulate latency
  await new Promise((r) => setTimeout(r, 50));

  const result: WarehouseWriteResult = {
    target,
    recordsWritten: enrichedEvents.length,
    writtenAt,
    eventIds,
  };

  console.log(
    `[writeToWarehouse] Done. ${result.recordsWritten} records written at ${result.writtenAt}`
  );
  return result;
}

// ─── Workflow entry point ─────────────────────────────────────────────────────

export const main = workflow(
  async (
    events: Array<{ id: string; type: string; payload: any }>,
    warehouseTarget: string = "main"
  ) => {
    // ── Step 1: Read previously processed event IDs from state file ───────────
    //
    // Wrapped in step() so the result is persisted and stable across replays.
    const processedIds = await step("read_processed_ids", () =>
      readProcessedIds()
    );

    console.log(
      `[etl_orchestrator] Loaded ${processedIds.length} previously processed IDs from state file.`
    );

    // ── Step 2: Deduplicate – filter out already-processed events ─────────────
    const processedIdSet = new Set(processedIds);
    const newEvents = events.filter((e) => !processedIdSet.has(e.id));
    const skippedCount = events.length - newEvents.length;

    console.log(
      `[etl_orchestrator] Total events received: ${events.length} | ` +
        `Duplicates skipped: ${skippedCount} | New events to process: ${newEvents.length}`
    );

    if (newEvents.length === 0) {
      return {
        status: "no_new_events",
        message: "All incoming events were already processed. Nothing to do.",
        totalReceived: events.length,
        duplicatesSkipped: skippedCount,
        newEventsProcessed: 0,
        warehouseTarget,
      };
    }

    // ── Step 3: Enrich new events in parallel (max 5 concurrent) ─────────────
    console.log(
      `[etl_orchestrator] Enriching ${newEvents.length} events (concurrency=5)…`
    );

    const enrichedEvents = await parallel(
      newEvents,
      (event) => task(enrichEvent)(event),
      { concurrency: 5 }
    );

    console.log(
      `[etl_orchestrator] Enrichment complete. ${enrichedEvents.length} events enriched.`
    );

    // ── Step 4: Obtain resume/approval URLs and request human approval ────────
    //
    // getResumeUrls() must be called inside step() for replay-safety:
    // on a replay the cached URL is returned instead of generating a new one.
    const resumeUrls = await step("get_approval_urls", () => getResumeUrls());

    // Log the URL so an operator can find it in the job logs.
    console.log(
      `[etl_orchestrator] ⏳ Human approval required before writing to warehouse="${warehouseTarget}".`
    );
    console.log(
      `[etl_orchestrator] 🔗 Approval page : ${resumeUrls.approvalPage}`
    );
    console.log(
      `[etl_orchestrator] ✅ Resume URL    : ${resumeUrls.resume}`
    );
    console.log(
      `[etl_orchestrator] ❌ Cancel URL    : ${resumeUrls.cancel}`
    );

    // ── Step 5: Suspend and wait for a human to approve or reject ─────────────
    //
    // waitForApproval() releases the worker slot entirely while suspended.
    // The workflow resumes only when an approve or reject event is received.
    const approval = await waitForApproval({
      timeout: 86400, // 24-hour window before auto-cancel
    });

    // ── Step 6: Branch on approval decision ───────────────────────────────────

    if (!approval.approved) {
      // ── Rejection path ────────────────────────────────────────────────────
      console.log(
        `[etl_orchestrator] ❌ Rejected by "${approval.approver}". Aborting warehouse write.`
      );

      return {
        status: "rejected",
        message: `ETL run rejected by approver "${approval.approver}". No data was written to the warehouse.`,
        rejectedBy: approval.approver,
        warehouseTarget,
        totalReceived: events.length,
        duplicatesSkipped: skippedCount,
        newEventsConsidered: newEvents.length,
        newEventsWritten: 0,
        enrichedEventSummary: enrichedEvents.map((e) => ({
          id: e.id,
          type: e.type,
          enrichedAt: e.enrichedAt,
        })),
      };
    }

    // ── Approval path ─────────────────────────────────────────────────────────
    console.log(
      `[etl_orchestrator] ✅ Approved by "${approval.approver}". Proceeding to warehouse write…`
    );

    // ── Step 7: Write enriched events to the data warehouse ───────────────────
    const writeResult = await task(writeToWarehouse)(
      enrichedEvents,
      warehouseTarget
    );

    // ── Step 8: Persist newly processed IDs to state file ────────────────────
    //
    // Merge old IDs with the IDs just written, then flush to disk.
    // Wrapped in step() so the file write is idempotent across replays.
    const updatedIds = await step("update_processed_ids", () => {
      const newIds = enrichedEvents.map((e) => e.id);
      const merged = Array.from(new Set([...processedIds, ...newIds]));
      writeProcessedIds(merged);
      console.log(
        `[etl_orchestrator] State file updated. Total processed IDs: ${merged.length}`
      );
      return merged;
    });

    // ── Step 9: Return success summary ────────────────────────────────────────
    return {
      status: "success",
      message: `ETL run completed successfully. ${writeResult.recordsWritten} events written to warehouse="${warehouseTarget}".`,
      approvedBy: approval.approver,
      warehouseTarget,
      totalReceived: events.length,
      duplicatesSkipped: skippedCount,
      newEventsProcessed: enrichedEvents.length,
      warehouseWrite: writeResult,
      totalStoredIds: updatedIds.length,
      enrichedEventSummary: enrichedEvents.map((e) => ({
        id: e.id,
        type: e.type,
        enrichedAt: e.enrichedAt,
        enrichmentMeta: e.enrichmentMeta,
      })),
    };
  }
);
