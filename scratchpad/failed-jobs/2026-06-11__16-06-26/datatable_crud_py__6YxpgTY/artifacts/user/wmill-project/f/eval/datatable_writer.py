import wmill

def main(records: list[dict]):
    db = wmill.datatable()
    
    # Create table if not exists
    db.query("""
        CREATE TABLE IF NOT EXISTS "eval_orders_zr-6yxpgty" (
            id INT PRIMARY KEY,
            status TEXT
        )
    """).execute()
    
    inserted = 0
    for record in records:
        db.query("""
            INSERT INTO "eval_orders_zr-6yxpgty" (id, status)
            VALUES ($1, $2)
        """, record["id"], record["status"]).execute()
        inserted += 1
        
    return {"inserted": inserted}
