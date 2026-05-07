export async function main(limit: number = 10): Promise<Array<{ id: number; name: string; email: string }>> {
  // Simulate fetching users (no real HTTP)
  return Array.from({ length: limit }, (_, i) => ({
    id: i + 1,
    name: `User ${i + 1}`,
    email: `user${i + 1}@example.com`
  }));
}