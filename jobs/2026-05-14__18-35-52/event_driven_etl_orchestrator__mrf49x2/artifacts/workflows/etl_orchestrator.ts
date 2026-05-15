type EventRecord = {
  id: string;
  type: string;
  payload: unknown;
};

type WorkflowInput = {
  events: EventRecord[];
  warehouseTarget?: string;
};

type WorkflowSummary = {
  status: "approved" | "rejected" | "noop";
  warehouseTarget: string;
  totalReceived: number;
  totalNew: number;
  approvalUrl?: string | null;
  processedEventIds: string[];
};

const PROCESSED_EVENTS_PATH = "/home/user/windmill-project/processed_events.json";
const ENRICH_TASK_PATH = "f/scripts/enrich_event";
const WAREHOUSE_TASK_PATH = "f/scripts/write_to_warehouse";
const MAX_CONCURRENCY = 5;

const wmill = (globalThis as { wmill?: Record<string, unknown> }).wmill as Record<string, any> | undefined;

const normalizeIds = (raw: unknown): string[] =>
  Array.isArray(raw) ? raw.filter((id): id is string => typeof id === "string") : [];

const readProcessedIds = async (): Promise<Set<string>> => {
  try {
    const contents = await Deno.readTextFile(PROCESSED_EVENTS_PATH);
    return new Set(normalizeIds(JSON.parse(contents)));
  } catch (error) {
    if (error instanceof Deno.errors.NotFound) {
      return new Set();
    }
    throw error;
  }
};

const writeProcessedIds = async (ids: Set<string>): Promise<void> => {
  const payload = JSON.stringify(Array.from(ids), null, 2);
  await Deno.writeTextFile(PROCESSED_EVENTS_PATH, `${payload}\n`);
};

const runWithConcurrency = async <T, R>(
  items: T[],
  limit: number,
  handler: (item: T, index: number) => Promise<R>,
): Promise<R[]> => {
  if (items.length === 0) {
    return [];
  }

  const results: R[] = new Array(items.length);
  let index = 0;

  const workers = Array.from({ length: Math.min(limit, items.length) }, async () => {
    while (index < items.length) {
      const current = index;
      index += 1;
      results[current] = await handler(items[current], current);
    }
  });

  await Promise.all(workers);
  return results;
};

const enrichEvent = async (event: EventRecord): Promise<unknown> => {
  if (!wmill?.runScript) {
    throw new Error("Windmill runScript API is unavailable.");
  }
  return await wmill.runScript(ENRICH_TASK_PATH, { event });
};

const writeToWarehouse = async (events: unknown[], warehouseTarget: string): Promise<void> => {
  if (!wmill?.runScript) {
    throw new Error("Windmill runScript API is unavailable.");
  }
  await wmill.runScript(WAREHOUSE_TASK_PATH, { events, warehouseTarget });
};

const requestApproval = async (approvalUrl: string | null, total: number, target: string): Promise<boolean> => {
  if (!wmill?.waitForApproval) {
    throw new Error("Windmill waitForApproval API is unavailable.");
  }
  return await wmill.waitForApproval({
    title: "Approve warehouse load",
    message: `Load ${total} enriched events into ${target}?`,
    approvalUrl,
  });
};

export default async function main({ events, warehouseTarget = "main" }: WorkflowInput): Promise<WorkflowSummary> {
  const processedIds = await readProcessedIds();
  const newEvents = events.filter((event) => !processedIds.has(event.id));

  if (newEvents.length === 0) {
    return {
      status: "noop",
      warehouseTarget,
      totalReceived: events.length,
      totalNew: 0,
      processedEventIds: [],
    };
  }

  const enrichedEvents = await runWithConcurrency(newEvents, MAX_CONCURRENCY, async (event) => {
    return await enrichEvent(event);
  });

  if (!wmill?.getResumeUrls) {
    throw new Error("Windmill getResumeUrls API is unavailable.");
  }

  const resumeUrls = await wmill.getResumeUrls();
  const approvalUrl = resumeUrls?.approval ?? resumeUrls?.approve ?? resumeUrls?.approvalUrl ?? null;
  console.log("Approval URL:", approvalUrl ?? "(unavailable)");

  const approved = await requestApproval(approvalUrl, enrichedEvents.length, warehouseTarget);

  if (!approved) {
    return {
      status: "rejected",
      warehouseTarget,
      totalReceived: events.length,
      totalNew: newEvents.length,
      approvalUrl,
      processedEventIds: [],
    };
  }

  await writeToWarehouse(enrichedEvents, warehouseTarget);

  const newlyProcessedIds = newEvents.map((event) => event.id);
  newlyProcessedIds.forEach((id) => processedIds.add(id));
  await writeProcessedIds(processedIds);

  return {
    status: "approved",
    warehouseTarget,
    totalReceived: events.length,
    totalNew: newEvents.length,
    approvalUrl,
    processedEventIds: newlyProcessedIds,
  };
}
