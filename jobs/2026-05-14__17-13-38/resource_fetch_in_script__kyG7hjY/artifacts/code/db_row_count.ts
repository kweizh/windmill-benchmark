type Postgresql = {
  host: string;
  port: number;
  user: string;
  dbname: string;
  sslmode: string;
  password: string;
};

export async function main(db: Postgresql, table_name: string) {
  return {
    host: db.host,
    dbname: db.dbname,
    table: table_name,
    query: `SELECT COUNT(*) FROM ${table_name}`,
    note: "Resource received successfully"
  };
}