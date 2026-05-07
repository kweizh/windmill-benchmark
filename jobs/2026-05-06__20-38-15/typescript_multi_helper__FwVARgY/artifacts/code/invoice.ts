function formatCurrency(amount: number, currency: string): string {
  return `${currency} ${amount.toFixed(2)}`;
}

function computeSubtotal(items: Array<{ qty: number; unit_price: number }>): number {
  return items.reduce((sum, item) => sum + item.qty * item.unit_price, 0);
}

export async function main(
  items: Array<{ name: string; qty: number; unit_price: number }>,
  tax_rate: number = 0.1,
  currency: string = "USD"
) {
  const subtotal = computeSubtotal(items);
  const tax = subtotal * tax_rate;
  const total = subtotal + tax;

  return {
    subtotal: formatCurrency(subtotal, currency),
    tax: formatCurrency(tax, currency),
    total: formatCurrency(total, currency),
    line_items: items.map((i) => ({
      name: i.name,
      amount: formatCurrency(i.qty * i.unit_price, currency),
    })),
  };
}
