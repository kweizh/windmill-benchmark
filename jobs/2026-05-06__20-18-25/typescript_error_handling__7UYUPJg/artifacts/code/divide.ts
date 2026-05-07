export async function main(numerator: number, denominator: number) {
  if (denominator === 0) {
    throw new Error("Division by zero is not allowed");
  }
  return { result: numerator / denominator, numerator, denominator };
}