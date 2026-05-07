// summary: "Count lines in text"
// language: typescript

export async function main(text: string) {
  return { line_count: text.split('\n').length };
}
