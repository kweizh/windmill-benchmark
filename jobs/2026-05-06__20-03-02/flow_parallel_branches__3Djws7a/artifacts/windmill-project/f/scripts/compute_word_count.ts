// summary: "Count words in text"
// language: typescript

export async function main(text: string) {
  return { word_count: text.trim().split(/\s+/).filter(w => w).length };
}
