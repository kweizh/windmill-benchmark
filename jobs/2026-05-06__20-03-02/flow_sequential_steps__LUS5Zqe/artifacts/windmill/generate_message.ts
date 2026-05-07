export async function main(name: string) {
  return { message: `Hello, ${name}!`, timestamp: new Date().toISOString() };
}
