export async function main(score: number) {
  return { score, passed: score >= 60 };
}
