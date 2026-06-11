import * as wmill from "windmill-client";
import { Client } from "pg";

type Postgresql = {
  host: string;
  port: number;
  user: string;
  dbname: string;
  sslmode: string;
  password: string;
  root_certificate_pem?: string;
};

export async function main(pg: Postgresql): Promise<{ count: number }> {
  const client = new Client({
    host: pg.host,
    port: pg.port,
    user: pg.user,
    database: pg.dbname,
    password: pg.password,
    ssl: pg.sslmode === "disable" ? false : { rejectUnauthorized: false },
  });

  try {
    await client.connect();
    const result = await client.query(
      "SELECT COUNT(*) AS n FROM information_schema.tables WHERE table_schema = 'public'"
    );
    const count = parseInt(result.rows[0].n, 10);
    return { count };
  } finally {
    await client.end();
  }
}