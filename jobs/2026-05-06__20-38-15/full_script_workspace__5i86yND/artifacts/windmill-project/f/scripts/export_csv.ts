export async function main(records: Array<Record<string, unknown>>, delimiter: string = ",") {
  if (records.length === 0) return { csv: "", row_count: 0 };
  const headers = Object.keys(records[0]);
  const rows = [headers.join(delimiter), ...records.map(r => headers.map(h => String(r[h] ?? '')).join(delimiter))];
  return { csv: rows.join("\n"), row_count: records.length };
}
