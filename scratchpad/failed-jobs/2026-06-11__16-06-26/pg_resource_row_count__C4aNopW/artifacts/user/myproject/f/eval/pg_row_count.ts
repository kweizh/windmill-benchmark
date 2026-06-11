import * as wmill from "windmill-client";
import { Client } from "pg";

export type Postgresql = {
  host: string;
  port: number;
  user: string;
  password?: string;
  dbname: string;
  sslmode?: string;
  root_certificate_pem?: string;
};

export async function main(pg: Postgresql) {
  let ssl: any = undefined;
  if (pg.sslmode && pg.sslmode !== "disable") {
    ssl = { rejectUnauthorized: false };
    if (pg.root_certificate_pem) {
      ssl.ca = pg.root_certificate_pem;
    }
  } else if (pg.sslmode === "disable") {
    ssl = false;
  }

  const client = new Client({
    host: pg.host,
    port: pg.port,
    user: pg.user,
    password: pg.password,
    database: pg.dbname,
    ssl: ssl,
  });

  await client.connect();
  try {
    const res = await client.query("SELECT COUNT(*) AS n FROM information_schema.tables WHERE table_schema = 'public'");
    return { count: parseInt(res.rows[0].n, 10) };
  } finally {
    await client.end();
  }
}
