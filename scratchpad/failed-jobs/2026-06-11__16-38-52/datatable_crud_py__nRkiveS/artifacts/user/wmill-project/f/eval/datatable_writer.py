import wmill


def main(records: list[dict]):
    db = wmill.datatable()

    # Create the table if it doesn't exist
    db.query(
        """
        CREATE TABLE IF NOT EXISTS eval_orders_zr-nrkives (
            id INT,
            status TEXT
        )
        """
    ).fetch()

    # Insert each record
    inserted = 0
    for record in records:
        db.query(
            "INSERT INTO eval_orders_zr-nrkives (id, status) VALUES ($1, $2)",
            record["id"],
            record["status"],
        ).fetch()
        inserted += 1

    return {"inserted": inserted}
