import wmill


def main(records: list[dict]) -> dict:
    db = wmill.datatable()
    table_name = "eval_orders_zr-uh49lsg"

    # Create the table if it doesn't exist
    db.query(
        f"CREATE TABLE IF NOT EXISTS {table_name} (id INT, status TEXT)"
    ).fetch(result_collection="all")

    # Insert each record
    for record in records:
        db.query(
            f"INSERT INTO {table_name} (id, status) VALUES ($1, $2)",
            record["id"],
            record["status"],
        ).fetch(result_collection="all")

    return {"inserted": len(records)}