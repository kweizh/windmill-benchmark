/**
 * Companion module: save_report
 * Logs the processing summary and returns a structured report object.
 *
 * Windmill WAC __mod pattern – this file is a standalone task script.
 * Reference from the parent workflow via
 * taskScript("f/workflows/data_processor/__mod/save_report").
 */
export interface ReportResult {
  total: number;
  status: "saved";
}

export async function main(results: any[]): Promise<ReportResult> {
  if (!Array.isArray(results)) {
    throw new Error("save_report: expected an array, got " + typeof results);
  }
  console.log(`Report: ${results.length} records processed`);
  return { total: results.length, status: "saved" };
}
