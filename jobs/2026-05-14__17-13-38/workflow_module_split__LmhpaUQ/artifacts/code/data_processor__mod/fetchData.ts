export async function main(url: string) {
  const resp = await fetch(url);
  return resp.json();
}