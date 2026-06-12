export async function main(a: number, b: number): Promise<{ sum: number }> {
  return { sum: a + b };
}