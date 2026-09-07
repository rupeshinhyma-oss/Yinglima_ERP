import io
import time
import psycopg2

OHIO_URL = "postgresql://neondb_owner:npg_7HTzR5qPbvmx@ep-old-fire-axzu5kp9-pooler.c-4.us-east-2.aws.neon.tech/yinglima_erp?sslmode=require"
SINGAPORE_URL = "postgresql://neondb_owner:npg_AGt9JDfwhW6y@ep-twilight-base-azwy3ofw-pooler.c-3.ap-southeast-1.aws.neon.tech/yinglima_erp?sslmode=require"

def main():
    start_time = time.time()
    print("=" * 75)
    print(">>> SHIFTING DATABASE FROM OHIO NEON TO SINGAPORE NEON")
    print("=" * 75)

    print("\n[1/5] Connecting to Ohio and Singapore...")
    s_conn = psycopg2.connect(OHIO_URL)
    s_cur = s_conn.cursor()
    d_conn = psycopg2.connect(SINGAPORE_URL)
    d_cur = d_conn.cursor()
    print("Connected successfully!")

    print("\n[2/5] Backing up and temporarily dropping foreign keys on Singapore...")
    d_cur.execute("""
        SELECT
            tc.constraint_name,
            tc.table_name,
            pg_get_constraintdef(c.oid) AS constraint_def
        FROM information_schema.table_constraints tc
        JOIN pg_constraint c ON c.conname = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY'
          AND tc.table_schema = 'public';
    """)
    fk_constraints = d_cur.fetchall()
    print(f"Found {len(fk_constraints)} FK constraints on destination.")

    for conname, tbl, _ in fk_constraints:
        try:
            d_cur.execute(f'ALTER TABLE "{tbl}" DROP CONSTRAINT IF EXISTS "{conname}";')
        except Exception:
            pass
    d_conn.commit()

    try:
        d_cur.execute('ALTER TABLE "products" ALTER COLUMN "product_code" DROP NOT NULL;')
        d_cur.execute('ALTER TABLE "users" ALTER COLUMN "status" TYPE VARCHAR(50);')
        d_cur.execute('ALTER TABLE "users" ALTER COLUMN "gender" TYPE VARCHAR(50);')
        d_conn.commit()
    except Exception:
        d_conn.rollback()

    s_cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
          AND table_type = 'BASE TABLE'
          AND table_name != 'alembic_version'
        ORDER BY table_name;
    """)
    tables = [r[0] for r in s_cur.fetchall()]
    print(f"\n[3/5] Tables to migrate: {len(tables)}")

    print("\n[4/5] Truncating destination tables on Singapore...")
    table_list = ", ".join(f'"{t}"' for t in tables)
    d_cur.execute(f'TRUNCATE TABLE {table_list} CASCADE;')
    d_conn.commit()
    print("All destination tables cleanly truncated.")

    print("\n[5/5] Streaming tables from Ohio to Singapore...")
    transferred = {}
    for idx, table in enumerate(tables, 1):
        s_cur.execute(f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = '{table}' AND table_schema = 'public'
            ORDER BY ordinal_position;
        """)
        s_cols = set(r[0] for r in s_cur.fetchall())

        d_cur.execute(f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = '{table}' AND table_schema = 'public'
            ORDER BY ordinal_position;
        """)
        d_cols = set(r[0] for r in d_cur.fetchall())

        common_cols = [c for c in s_cols if c in d_cols]
        if not common_cols:
            continue

        col_list = ", ".join(f'"{c}"' for c in common_cols)
        buf = io.BytesIO()

        s_cur.copy_expert(f'COPY (SELECT {col_list} FROM "{table}") TO STDOUT WITH (FORMAT binary);', buf)
        byte_size = buf.getbuffer().nbytes
        buf.seek(0)

        if byte_size > 0:
            d_cur.copy_expert(f'COPY "{table}" ({col_list}) FROM STDIN WITH (FORMAT binary);', buf)
            d_conn.commit()

        d_cur.execute(f'SELECT count(*) FROM "{table}";')
        res = d_cur.fetchone()
        cnt = int(res[0]) if res is not None else 0
        transferred[table] = cnt
        print(f"  [{idx:2d}/{len(tables)}] {table:32s} -> {cnt:>6d} rows ({byte_size / 1024:.1f} KB)", flush=True)

    print("\nRecreating foreign keys on Singapore...")
    recreated = 0
    for conname, tbl, condef in fk_constraints:
        try:
            d_cur.execute(f'ALTER TABLE "{tbl}" ADD CONSTRAINT "{conname}" {condef};')
            d_conn.commit()
            recreated += 1
        except Exception:
            d_conn.rollback()

    print(f"Re-applied {recreated}/{len(fk_constraints)} foreign keys.")

    d_cur.execute("""
        SELECT 
            s.relname AS seq_name,
            t.relname AS table_name,
            a.attname AS column_name
        FROM pg_class s
        JOIN pg_depend d ON d.objid = s.oid
        JOIN pg_class t ON d.refobjid = t.oid
        JOIN pg_attribute a ON (d.refobjid, d.refobjsubid) = (a.attrelid, a.attnum)
        WHERE s.relkind = 'S' AND t.relkind = 'r' AND s.relnamespace = 'public'::regnamespace;
    """)
    sequences = d_cur.fetchall()
    for seq_name, table_name, column_name in sequences:
        try:
            d_cur.execute(f"""
                SELECT setval('"{seq_name}"', COALESCE((SELECT MAX("{column_name}") FROM "{table_name}"), 1));
            """)
        except Exception:
            pass
    d_conn.commit()

    total_rows = sum(transferred.values())
    elapsed = time.time() - start_time
    print("\n" + "=" * 75)
    print(f">>> SHIFT TO SINGAPORE NEON COMPLETE in {elapsed:.1f}s!")
    print(f">>> Total rows in Singapore [yinglima_erp]: {total_rows:,}")
    print("=" * 75)

    s_conn.close()
    d_conn.close()

if __name__ == "__main__":
    main()
