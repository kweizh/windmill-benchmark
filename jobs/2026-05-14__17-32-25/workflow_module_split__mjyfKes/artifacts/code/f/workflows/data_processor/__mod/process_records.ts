/**
 * Companion module: process_records
 * Transforms an array of raw records by stamping each item with
 * `processed: true` and annotating it with the total count.
 *
 * Windmill WAC __mod pattern – this file is a standalone task script.
 * Reference from the parent workflow via
 * taskScript("f/workflows/data_processor/__mod/process_records").
 */
export async function main(data: any[]): Promise<any[]> {
  if (!Array.isArray(data)) {
    throw new Error("process_records: expected an array, got " + typeof data);
  }
  return data.map((item) => ({
    ...item,
    processed: true,
    count: data.length,
  }));
}
