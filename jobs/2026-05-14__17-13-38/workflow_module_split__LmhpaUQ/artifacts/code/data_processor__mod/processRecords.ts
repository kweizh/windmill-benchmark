export async function main(data: any[]) {
  return data.map(item => ({ ...item, processed: true, count: data.length }));
}