import * as wmill from "windmill-client";
import { Client } from "pg";

export interface Postgresql {
  host: string;
  port: number;
  user: string;
  dbname: string;
  sslmode: string;
  password: string;
  root_certificate_pem?: string;
}

export async function main(pg: Postgresql) {
  const baseConfig = {
    host: pg.host,
    port: pg.port,
    user: pg.user,
    database: pg.dbname,
    password: pg.password,
  };

  // sslmode "prefer" means try SSL first, fall back to plain if unsupported
  const trySsl = pg.sslmode !== "disable";
  let client: Client | null = null;

  if (trySsl) {
    try {
      client = new Client({ ...baseConfig, ssl: { rejectUnauthorized: false } });
      await client.connect();
    } catch {
      await client?.end().catch(() => {});
      client = null;
    }
  }

  if (!client) {
    client = new Client({ ...baseConfig, ssl: false });
    await client.connect();
  }

  try {
    const result = await client.query(
      "SELECT COUNT(*) AS n FROM information_schema.tables WHERE table_schema = 'public'"
    );
    const count = parseInt(result.rows[0].n, 10);
    return { count };
  } finally {
    await client.end();
  }
}
