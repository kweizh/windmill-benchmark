export async function main(
  title: string,
  items: string[],
  footer: string = "End of report"
) {
  const lines = [
    `=== ${title} ===`,
    ...items.map((item) => `- ${item}`),
    `--- ${footer} ---`,
  ];
  return lines.join("\n");
}
