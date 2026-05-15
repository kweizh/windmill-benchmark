/**
 * Companion module: fetch_data
 * Fetches raw JSON data from the given URL.
 *
 * Windmill WAC __mod pattern – this file is a standalone task script.
 * It exports `main` so that the parent workflow can reference it via
 * taskScript("f/workflows/data_processor/__mod/fetch_data").
 */
export async function main(url: string): Promise<any> {
  const resp = await fetch(url);
  if (!resp.ok) {
    throw new Error(`fetch_data: HTTP ${resp.status} for ${url}`);
  }
  return resp.json();
}
