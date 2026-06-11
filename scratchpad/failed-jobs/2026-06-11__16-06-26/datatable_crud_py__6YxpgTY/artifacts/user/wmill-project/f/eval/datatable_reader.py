import wmill

def main():
    db = wmill.datatable()
    
    rows = db.query("""
        SELECT id, status FROM "eval_orders_zr-6yxpgty" ORDER BY id ASC
    """).fetch()
    
    return {"rows": rows}
