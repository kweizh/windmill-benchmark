import wmill


def main() -> dict:
    db = wmill.datatable()
    table_name = "eval_orders_zr-uh49lsg"

    rows = db.query(
        f"SELECT id, status FROM {table_name} ORDER BY id ASC"
    ).fetch()

    return {"rows": [{"id": row["id"], "status": row["status"]} for row in rows]}