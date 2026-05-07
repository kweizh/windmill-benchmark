export async function main(
  users: Array<{ id: number; name: string; active: boolean }>,
  active_only: boolean = true
) {
  const filtered = active_only ? users.filter(u => u.active) : users;
  return filtered.map(u => ({ id: u.id, name: u.name, display: `#${u.id} — ${u.name}` }));
}