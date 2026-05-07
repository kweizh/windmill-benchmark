export async function main(iso_date: string, label: string = "Event") {
  const target = new Date(iso_date);
  const today = new Date(new Date().toISOString().split('T')[0]);
  const days_from_today = Math.round((target.getTime() - today.getTime()) / 86400000);
  return {
    label,
    formatted: target.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }),
    iso: iso_date,
    days_from_today,
  };
}