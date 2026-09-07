import psycopg2

NEON_CONN = "postgresql://neondb_owner:npg_AGt9JDfwhW6y@ep-twilight-base-azwy3ofw-pooler.c-3.ap-southeast-1.aws.neon.tech/yinglima_erp?sslmode=require"

def sync_seqs():
    conn = psycopg2.connect(NEON_CONN)
    cur = conn.cursor()
    cur.execute("""
        SELECT table_name, column_name, column_default 
        FROM information_schema.columns 
        WHERE table_schema = 'public' AND column_default LIKE 'nextval%';
    """)
    seq_cols = cur.fetchall()
    print(f"Syncing {len(seq_cols)} sequences in Neon...")
    for tbl, col, default in seq_cols:
        seq_name = default.split("'::")[0].split("nextval('")[-1]
        cur.execute(f'SELECT coalesce(max("{col}"), 0) FROM "{tbl}";')
        row = cur.fetchone()
        max_val = row[0] if row is not None else 0
        if max_val > 0:
            cur.execute(f"SELECT setval('{seq_name}', {max_val}, true);")
            print(f"  {seq_name} -> {max_val}")
    conn.commit()
    print("All sequences synced!")
    conn.close()

if __name__ == "__main__":
    sync_seqs()
