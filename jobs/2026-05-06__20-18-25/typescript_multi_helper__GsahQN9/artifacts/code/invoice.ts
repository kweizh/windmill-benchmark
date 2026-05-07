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
  
  return {
    subtotal: formatCurrency(subtotal, currency),
    tax: formatCurrency(subtotal * tax_rate, currency),
    total: formatCurrency(subtotal * (1 + tax_rate), currency),
    line_items: items.map(i => ({
      name: i.name,
      amount: formatCurrency(i.qty * i.unit_price, currency)
    }))
  };
}