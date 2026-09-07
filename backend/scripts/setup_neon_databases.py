"""
Neon 3-Database Setup & Migration Utility.

Automates migrations and bootstrap seeding across the three company databases on Neon:
1. yinglima_erp (China procurement / export)
2. inhyma_erp   (India distribution / import)
3. erp_main     (Central / Master template)

Usage:
    python -m scripts.setup_neon_databases --url "<NEON_CONNECTION_STRING>"
    python -m scripts.setup_neon_databases --all
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse, urlunparse

BACKEND_DIR = Path(__file__).resolve().parent.parent

DATABASES = ["yinglima_erp", "inhyma_erp", "erp_main"]


def normalize_asyncpg_url(url: str) -> str:
    """Ensure the URL has the postgresql+asyncpg:// driver prefix and ssl=require."""
    url = url.strip().strip("'\"")
    if url.startswith("postgres://"):
        url = "postgresql+asyncpg://" + url[len("postgres://"):]
    elif url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
        url = "postgresql+asyncpg://" + url[len("postgresql://"):]
    
    parsed = urlparse(url)
    return urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        "ssl=require",
        parsed.fragment
    ))


def derive_database_url(base_url: str, target_db_name: str) -> str:
    """Replace the database path in the connection URL with the target database name."""
    clean_url = normalize_asyncpg_url(base_url)
    parsed = urlparse(clean_url)
    
    # Path is e.g. /neondb or /yinglima_erp
    new_path = f"/{target_db_name}"
    derived = urlunparse((
        parsed.scheme,
        parsed.netloc,
        new_path,
        parsed.params,
        parsed.query,
        parsed.fragment
    ))
    return derived


def run_migration_for_db(db_url: str, db_name: str) -> bool:
    """Run Alembic upgrade head and scripts.seed against the given database."""
    print(f"\n{'=' * 70}")
    print(f">>> Migrating and Seeding Database: [{db_name}]")
    print(f"{'=' * 70}")
    
    env = os.environ.copy()
    env["DATABASE_URL"] = db_url
    env["DATABASE_DISABLE_STATEMENT_CACHE"] = "true"
    python_exe = sys.executable

    # 1. Alembic upgrade head
    print(f"\n[1/2] Running alembic upgrade head on {db_name}...")
    res_alembic = subprocess.run([python_exe, "-m", "alembic", "upgrade", "head"], cwd=BACKEND_DIR, env=env)
    if res_alembic.returncode != 0:
        print(f"ERROR: Alembic migration failed for {db_name} (code {res_alembic.returncode})")
        return False

    # 2. Seed script
    print(f"\n[2/2] Running scripts.seed on {db_name}...")
    res_seed = subprocess.run([python_exe, "-m", "scripts.seed"], cwd=BACKEND_DIR, env=env)
    if res_seed.returncode != 0:
        print(f"ERROR: Seed failed for {db_name} (code {res_seed.returncode})")
        return False

    print(f"\n>>> SUCCESS: Database [{db_name}] is fully migrated and seeded!")
    return True


def create_env_file_for_db(db_url: str, db_name: str) -> Path:
    """Create a copy of .env configured for this specific database."""
    env_file = BACKEND_DIR / f".env.{db_name}"
    base_env = BACKEND_DIR / ".env"
    
    content = ""
    if base_env.exists():
        content = base_env.read_text(encoding="utf-8")
    else:
        example_env = BACKEND_DIR / ".env.example"
        if example_env.exists():
            content = example_env.read_text(encoding="utf-8")

    lines = content.splitlines()
    new_lines = []
    found_db_url = False
    found_cache = False

    for line in lines:
        if line.startswith("DATABASE_URL="):
            new_lines.append(f"DATABASE_URL={db_url}")
            found_db_url = True
        elif line.startswith("DATABASE_DISABLE_STATEMENT_CACHE="):
            new_lines.append("DATABASE_DISABLE_STATEMENT_CACHE=true")
            found_cache = True
        elif line.startswith("APP_NAME="):
            new_lines.append(f"APP_NAME=ERP Backend ({db_name})")
        else:
            new_lines.append(line)

    if not found_db_url:
        new_lines.append(f"DATABASE_URL={db_url}")
    if not found_cache:
        new_lines.append("DATABASE_DISABLE_STATEMENT_CACHE=true")

    env_file.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    print(f"Saved configuration file: {env_file.name}")
    return env_file


def main():
    parser = argparse.ArgumentParser(description="Setup, migrate, and seed Neon databases.")
    parser.add_argument("--url", help="Any Neon connection string from your project.")
    parser.add_argument("--db", choices=DATABASES, help="Target a specific database only.")
    parser.add_argument("--all", action="store_true", help="Migrate and seed all 3 databases.")
    args = parser.parse_args()

    url = args.url or os.environ.get("DATABASE_URL")
    if not url:
        print("ERROR: Please provide a Neon connection string via --url or DATABASE_URL.")
        sys.exit(1)

    targets = [args.db] if args.db else DATABASES

    print(f"Starting Neon multi-database setup for targets: {targets}")
    successes = []

    for db_name in targets:
        target_url = derive_database_url(url, db_name)
        create_env_file_for_db(target_url, db_name)
        ok = run_migration_for_db(target_url, db_name)
        if ok:
            successes.append(db_name)

    print("\n" + "=" * 70)
    print(f"COMPLETED: {len(successes)}/{len(targets)} databases migrated successfully: {successes}")
    print("=" * 70)

    # Set yinglima_erp as active default in .env
    active_env = BACKEND_DIR / ".env.yinglima_erp"
    if active_env.exists():
        import shutil
        shutil.copyfile(active_env, BACKEND_DIR / ".env")
        print("\n>>> Active [backend/.env] successfully set to: yinglima_erp")


if __name__ == "__main__":
    main()
