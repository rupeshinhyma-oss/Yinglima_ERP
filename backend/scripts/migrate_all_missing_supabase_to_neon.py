import io
import psycopg2

SUPA_CONN = "postgresql://postgres:Inhyma%402026@db.mpvzjzunkiqchhhvxrza.supabase.co:5432/postgres?sslmode=require"
NEON_CONN = "postgresql://neondb_owner:npg_AGt9JDfwhW6y@ep-twilight-base-azwy3ofw-pooler.c-3.ap-southeast-1.aws.neon.tech/yinglima_erp?sslmode=require"

TASK_TABLES = [
    "notifications",
    "task_sprints",
    "task_templates",
    "task_labels",
    "tasks",
    "task_subtasks",
    "task_assignees",
    "task_subtask_assignees",
    "task_comments",
    "task_subtask_comments",
    "task_attachments",
    "task_subtask_attachments",
    "task_comment_attachments",
    "task_dependencies",
    "task_escalations",
    "task_escalation_comments",
    "task_label_links",
    "task_mentions",
    "task_reactions",
    "task_saved_filters",
    "task_voice_notes",
]

def get_table_ddl(cur, table_name):
    cur.execute("""
        SELECT 
            column_name, 
            data_type, 
            character_maximum_length,
            numeric_precision,
            numeric_scale,
            is_nullable,
            column_default,
            udt_name
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = %s
        ORDER BY ordinal_position;
    """, (table_name,))
    cols = cur.fetchall()

    col_defs = []
    for c in cols:
        name, dtype, char_len, num_prec, num_scale, nullable, default, udt = c
        col_type = dtype.upper()
        if dtype == 'USER-DEFINED':
            col_type = udt
        elif dtype == 'character varying':
            col_type = f"VARCHAR({char_len})" if char_len else "VARCHAR"
        elif dtype == 'character':
            col_type = f"CHAR({char_len})" if char_len else "CHAR"
        elif dtype == 'numeric' and num_prec:
            col_type = f"NUMERIC({num_prec},{num_scale or 0})"
        elif dtype == 'timestamp with time zone':
            col_type = "TIMESTAMPTZ"
        elif dtype == 'timestamp without time zone':
            col_type = "TIMESTAMP"
        
        null_clause = "NOT NULL" if nullable == "NO" else "NULL"
        default_clause = f"DEFAULT {default}" if default else ""
        col_defs.append(f'    "{name}" {col_type} {null_clause} {default_clause}'.strip())

    cur.execute("""
        SELECT c.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.constraint_column_usage ccu ON tc.constraint_name = ccu.constraint_name
        JOIN information_schema.key_column_usage c ON tc.constraint_name = c.constraint_name
        WHERE tc.constraint_type = 'PRIMARY KEY' AND tc.table_schema = 'public' AND tc.table_name = %s;
    """, (table_name,))
    pks = [f'"{r[0]}"' for r in cur.fetchall()]
    if pks:
        col_defs.append(f"    PRIMARY KEY ({', '.join(pks)})")

    ddl = f'CREATE TABLE IF NOT EXISTS "{table_name}" (\n' + ",\n".join(col_defs) + "\n);"
    return ddl

def migrate_missing_tables():
    s_conn = psycopg2.connect(SUPA_CONN)
    n_conn = psycopg2.connect(NEON_CONN)
    s_cur = s_conn.cursor()
    n_cur = n_conn.cursor()

    print("Step 1: Creating missing tables on Neon...")
    for t in TASK_TABLES:
        ddl = get_table_ddl(s_cur, t)
        print(f"Creating table {t}...")
        n_cur.execute(ddl)
    n_conn.commit()
    print("All tables created successfully!")

    print("\nStep 2: Copying rows for each task table...")
    for t in TASK_TABLES:
        s_cur.execute(f"SELECT count(*) FROM {t};")
        row = s_cur.fetchone()
        cnt = row[0] if row is not None else 0
        if cnt == 0:
            print(f"Table {t} has 0 rows, skipping copy.")
            continue

        print(f"Copying {cnt} rows for {t}...")
        buf = io.StringIO()
        s_cur.copy_expert(f'COPY "{t}" TO STDOUT (FORMAT CSV, HEADER)', buf)
        buf.seek(0)
        n_cur.execute(f'TRUNCATE TABLE "{t}" CASCADE;')
        n_cur.copy_expert(f'COPY "{t}" FROM STDIN (FORMAT CSV, HEADER)', buf)
        n_conn.commit()
        print(f"Successfully copied {cnt} rows for {t}.")

    print("\nStep 3: Adding missing columns to countries and products...")
    n_cur.execute("""
        ALTER TABLE countries ADD COLUMN IF NOT EXISTS iso2 VARCHAR(2);
        ALTER TABLE countries ADD COLUMN IF NOT EXISTS iso3 VARCHAR(3);
        ALTER TABLE products ADD COLUMN IF NOT EXISTS supplier_id UUID;
        ALTER TABLE products ADD COLUMN IF NOT EXISTS packaging_length NUMERIC;
        ALTER TABLE products ADD COLUMN IF NOT EXISTS packaging_width NUMERIC;
        ALTER TABLE products ADD COLUMN IF NOT EXISTS packaging_height NUMERIC;
        ALTER TABLE products ADD COLUMN IF NOT EXISTS packaging_weight NUMERIC;
        ALTER TABLE products ADD COLUMN IF NOT EXISTS master_box_qty INTEGER;
    """)
    n_conn.commit()

    print("Step 4: Syncing country iso2 and iso3 codes...")
    s_cur.execute("SELECT id, iso2, iso3 FROM countries WHERE iso2 IS NOT NULL OR iso3 IS NOT NULL;")
    countries_to_update = s_cur.fetchall()
    print(f"Updating {len(countries_to_update)} countries with iso codes...")
    for cid, iso2, iso3 in countries_to_update:
        n_cur.execute("UPDATE countries SET iso2 = %s, iso3 = %s WHERE id = %s;", (iso2, iso3, cid))
    n_conn.commit()

    print("Step 5: Syncing inquiry_messages...")
    buf = io.StringIO()
    s_cur.copy_expert('COPY "inquiry_messages" TO STDOUT (FORMAT CSV, HEADER)', buf)
    buf.seek(0)
    n_cur.execute('TRUNCATE TABLE "inquiry_messages" CASCADE;')
    n_cur.copy_expert('COPY "inquiry_messages" FROM STDIN (FORMAT CSV, HEADER)', buf)
    n_conn.commit()
    print("Inquiry messages copied successfully!")

    s_conn.close()
    n_conn.close()
    print("\nAll missing tables, columns, and data migrated to Neon successfully!")

if __name__ == "__main__":
    migrate_missing_tables()
