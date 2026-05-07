export async function main(id: number, name: string, active: boolean = true) {
  return {
    id,
    name,
    active,
    display: `[${id}] ${name} (${active ? 'active' : 'inactive'})`,
  };
}
