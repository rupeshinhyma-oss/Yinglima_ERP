import json
import psycopg2
from psycopg2.extras import DictCursor

SUPA_HOST = "db.mpvzjzunkiqchhhvxrza.supabase.co"
SUPA_PORT = 5432
SUPA_USER = "postgres"
SUPA_PASS = "Inhyma@2026"
SUPA_DB = "postgres"

NEON_CONN = "postgresql://neondb_owner:npg_AGt9JDfwhW6y@ep-twilight-base-azwy3ofw-pooler.c-3.ap-southeast-1.aws.neon.tech/yinglima_erp?sslmode=require"

def get_tables(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
              AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        return [r[0] for r in cur.fetchall()]

def get_row_count(conn, table):
    with conn.cursor() as cur:
        try:
            cur.execute(f'SELECT count(*) FROM "{table}";')
            return cur.fetchone()[0]
        except Exception as e:
            conn.rollback()
            return f"Error: {e}"

def get_columns(conn, table):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s
            ORDER BY column_name;
        """, (table,))
        return {r[0]: (r[1], r[2]) for r in cur.fetchall()}

def get_foreign_keys(conn, table):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT tc.constraint_name, kcu.column_name, ccu.table_name AS foreign_table_name, ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema = 'public' AND tc.table_name = %s;
        """, (table,))
        return cur.fetchall()

def main():
    s_conn = psycopg2.connect(
        host=SUPA_HOST, port=SUPA_PORT, user=SUPA_USER, password=SUPA_PASS, dbname=SUPA_DB, sslmode="require"
    )
    n_conn = psycopg2.connect(NEON_CONN)

    s_tables = set(get_tables(s_conn))
    n_tables = set(get_tables(n_conn))

    all_tables = sorted(list(s_tables | n_tables))

    print(f"Total tables in Supabase: {len(s_tables)}")
    print(f"Total tables in Neon:     {len(n_tables)}")
    print("=" * 80)
    print(f"{'Table Name':<35} | {'Supabase Rows':<15} | {'Neon Rows':<15} | {'Status':<10}")
    print("-" * 80)

    missing_in_neon = []
    missing_in_supa = []
    row_diffs = []
    col_diffs = {}

    for t in all_tables:
        in_s = t in s_tables
        in_n = t in n_tables

        s_rows = get_row_count(s_conn, t) if in_s else "-"
        n_rows = get_row_count(n_conn, t) if in_n else "-"

        status = "MATCH"
        if not in_n:
            status = "MISSING_IN_NEON"
            missing_in_neon.append(t)
        elif not in_s:
            status = "EXTRA_IN_NEON"
            missing_in_supa.append(t)
        elif s_rows != n_rows:
            status = "ROW_DIFF"
            row_diffs.append((t, s_rows, n_rows))

        print(f"{t:<35} | {str(s_rows):<15} | {str(n_rows):<15} | {status:<10}")

        # Check columns if in both
        if in_s and in_n:
            s_cols = get_columns(s_conn, t)
            n_cols = get_columns(n_conn, t)
            missing_cols_in_n = set(s_cols.keys()) - set(n_cols.keys())
            extra_cols_in_n = set(n_cols.keys()) - set(s_cols.keys())
            if missing_cols_in_n or extra_cols_in_n:
                col_diffs[t] = {
                    "missing_in_neon": list(missing_cols_in_n),
                    "extra_in_neon": list(extra_cols_in_n)
                }

    print("=" * 80)
    print("\n--- SUMMARY AUDIT RESULTS ---")
    print(f"Tables Missing in Neon: {missing_in_neon}")
    print(f"Tables Extra in Neon (New Modules): {missing_in_supa}")
    print(f"Tables with Row Differences: {row_diffs}")
    print(f"Column Differences: {json.dumps(col_diffs, indent=2)}")

    s_conn.close()
    n_conn.close()

if __name__ == "__main__":
    main()
