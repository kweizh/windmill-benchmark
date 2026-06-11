import * as wmill from "windmill-client";
import { Client } from "pg";

export type Postgresql = {
  host: string;
  port: number;
  user: string;
  dbname: string;
  sslmode: string;
  password?: string;
  root_certificate_pem?: string;
};

export async function main(pg: Postgresql) {
  let client: Client;

  const tryConnect = async (useSsl: boolean) => {
    const c = new Client({
      host: pg.host,
      port: pg.port,
      user: pg.user,
      password: pg.password,
      database: pg.dbname,
      ssl: useSsl
        ? {
            rejectUnauthorized: false,
            ca: pg.root_certificate_pem || undefined,
          }
        : false,
    });
    await c.connect();
    return c;
  };

  const useSslInitial = pg.sslmode && pg.sslmode !== "disable";

  try {
    client = await tryConnect(useSslInitial);
  } catch (err: any) {
    const isSslError = err.message?.includes("SSL") || err.message?.includes("support");
    if (useSslInitial && pg.sslmode === "prefer" && isSslError) {
      client = await tryConnect(false);
    } else {
      throw err;
    }
  }

  try {
    const res = await client.query(
      "SELECT COUNT(*) AS n FROM information_schema.tables WHERE table_schema = 'public'"
    );
    const count = parseInt(res.rows[0].n, 10);
    return { count };
  } finally {
    await client.end();
  }
}
