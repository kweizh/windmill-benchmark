/**
 * Workflow: data_processor
 *
 * Refactored to the Windmill WAC companion-module pattern (__mod/ folder).
 * Each step delegates to a dedicated task script living under
 * f/workflows/data_processor/__mod/.  The workflow itself contains no
 * business logic – it only orchestrates execution order and wires
 * inputs / outputs between steps.
 *
 * Step scripts:
 *   __mod/fetch_data.ts       – HTTP fetch → raw JSON array
 *   __mod/process_records.ts  – stamp each record with metadata
 *   __mod/save_report.ts      – log summary and return report object
 */
import { taskScript, workflow } from "windmill-client";

export const main = workflow(async (url: string) => {
  // Step 1 – fetch raw data from the supplied URL
  const rawData = await taskScript(
    "f/workflows/data_processor/__mod/fetch_data"
  )(url);

  // Step 2 – process / enrich every record
  const processed = await taskScript(
    "f/workflows/data_processor/__mod/process_records"
  )(rawData);

  // Step 3 – persist / report results
  return await taskScript(
    "f/workflows/data_processor/__mod/save_report"
  )(processed);
});
