"""
Restore Foreign Keys on Neon from Supabase Schema
=================================================
Reads all foreign key constraint definitions from Supabase and applies
them to Neon yinglima_erp.
"""

import psycopg2

SUPABASE_URL = "postgresql://postgres.mpvzjzunkiqchhhvxrza:Inhyma%402026@aws-0-ap-south-1.pooler.supabase.com:5432/postgres?sslmode=require"
NEON_URL = "postgresql://neondb_owner:npg_7HTzR5qPbvmx@ep-old-fire-axzu5kp9-pooler.c-4.us-east-2.aws.neon.tech/yinglima_erp?sslmode=require"


def restore_fks():
    print("Connecting to Supabase to read foreign key constraints...")
    s_conn = psycopg2.connect(SUPABASE_URL)
    s_cur = s_conn.cursor()

    s_cur.execute("""
        SELECT 
            conname, 
            conrelid::regclass::text AS tbl, 
            pg_get_constraintdef(c.oid) AS condef
        FROM pg_constraint c 
        WHERE contype = 'f' AND connamespace = 'public'::regnamespace;
    """)
    s_fks = s_cur.fetchall()
    s_conn.close()
    print(f"Read {len(s_fks)} foreign key constraints from Supabase.")

    print("\nConnecting to Neon to check and restore foreign key constraints...")
    n_conn = psycopg2.connect(NEON_URL)
    n_cur = n_conn.cursor()

    # Get existing Neon FKs
    n_cur.execute("SELECT conname FROM pg_constraint WHERE contype = 'f' AND connamespace = 'public'::regnamespace;")
    existing_fks = set(r[0] for r in n_cur.fetchall())
    print(f"Neon currently has {len(existing_fks)} active foreign keys.")

    # Get Neon base tables
    n_cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
    neon_tables = set(r[0] for r in n_cur.fetchall())

    success = 0
    skipped = 0
    failed = []

    for conname, tbl, condef in s_fks:
        if tbl not in neon_tables:
            skipped += 1
            continue
        if conname in existing_fks:
            skipped += 1
            continue

        try:
            n_cur.execute(f'ALTER TABLE "{tbl}" ADD CONSTRAINT "{conname}" {condef};')
            n_conn.commit()
            success += 1
        except Exception as exc:
            n_conn.rollback()
            failed.append((tbl, conname, str(exc).strip()))

    print(f"\nFK Restoration Summary:")
    print(f"  Added:   {success}")
    print(f"  Skipped: {skipped} (already present or table obsolete)")
    print(f"  Failed:  {len(failed)}")
    for tbl, conname, err in failed:
        print(f"    - {tbl}.{conname}: {err}")

    n_conn.close()


if __name__ == "__main__":
    restore_fks()
