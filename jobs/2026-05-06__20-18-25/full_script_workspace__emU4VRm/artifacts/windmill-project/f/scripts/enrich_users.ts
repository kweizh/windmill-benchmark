export async function main(
  users: Array<{ id: number; name: string; email: string }>,
  domain_filter: string = ""
) {
  const filtered = domain_filter
    ? users.filter(u => u.email.endsWith(domain_filter))
    : users;
  return filtered.map(u => ({ ...u, display: `[${u.id}] ${u.name} <${u.email}>` }));
}