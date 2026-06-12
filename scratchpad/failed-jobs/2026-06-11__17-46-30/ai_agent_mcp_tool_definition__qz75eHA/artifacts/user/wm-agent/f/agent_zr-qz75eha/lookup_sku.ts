// Tool script: lookup_sku
// Returns unit price and currency for a given product SKU

export async function main(sku: string): Promise<{ sku: string; unit_price: number; currency: string }> {
  // Simulated product catalog
  const catalog: Record<string, { unit_price: number; currency: string }> = {
    "WIDGET-42": { unit_price: 9.99, currency: "USD" },
    "GADGET-01": { unit_price: 24.99, currency: "USD" },
    "GIZMO-7": { unit_price: 4.99, currency: "USD" },
    "DOOHICKEY-99": { unit_price: 149.95, currency: "USD" },
    "THINGAMAJIG-5": { unit_price: 59.99, currency: "USD" },
  };

  const entry = catalog[sku.toUpperCase()];
  if (entry) {
    return { sku: sku.toUpperCase(), unit_price: entry.unit_price, currency: entry.currency };
  }

  // Default fallback for unknown SKUs
  return { sku: sku.toUpperCase(), unit_price: 0.0, currency: "USD" };
}
