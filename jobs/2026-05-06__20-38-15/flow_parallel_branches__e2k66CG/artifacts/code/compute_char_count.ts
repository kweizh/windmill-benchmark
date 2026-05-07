export async function main(text: string) {
  return { char_count: text.length, char_count_no_spaces: text.replace(/\s/g, '').length };
}
