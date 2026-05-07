// summary: "Check if a score passes"
// language: typescript
export async function main(score: number) {
  return { score, passed: score >= 60 };
}
