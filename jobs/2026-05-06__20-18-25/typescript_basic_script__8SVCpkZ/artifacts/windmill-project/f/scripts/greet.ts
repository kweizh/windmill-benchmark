export async function main(name: string, greeting: string = "Hello") {
  return `${greeting}, ${name}!`;
}