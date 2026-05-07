export async function main(
  products: Array<{ id: number; name: string; price: number }>,
  tax_rate: number = 0.1
) {
  const enriched = await Promise.all(
    products.map(async (p) => ({
      ...p,
      tax: parseFloat((p.price * tax_rate).toFixed(2)),
      total: parseFloat((p.price * (1 + tax_rate)).toFixed(2)),
      label: `${p.name} ($${p.price})`,
    }))
  );
  return { count: enriched.length, tax_rate, products: enriched };
}
