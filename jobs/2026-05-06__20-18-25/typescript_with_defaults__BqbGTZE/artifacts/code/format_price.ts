export async function main(
  amount: number,
  currency: string = "USD",
  decimals: number = 2,
  prefix: string = ""
) {
  return `${prefix}${amount.toFixed(decimals)} ${currency}`;
}