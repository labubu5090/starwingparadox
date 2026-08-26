"""Utility script to connect to a PostgreSQL database and document the schema.

Usage:
    python scripts/inspect_legacy_schema.py --database-url "postgresql://paradox:changeme@localhost:5432/paradox"

This script is used for forensic comparison between the legacy schema and
the Python server's SQLAlchemy models.
"""

import argparse
import sys
from dataclasses import dataclass

try:
    import psycopg
except ImportError:
    print("Error: psycopg not installed. Run: pip install psycopg[binary]")
    sys.exit(1)


@dataclass
class ColumnInfo:
    table_name: str
    column_name: str
    data_type: str
    is_nullable: str
    column_default: str | None


@dataclass
class TableInfo:
    schema_name: str
    table_name: str
    table_type: str


def inspect_schema(database_url: str) -> None:
    """Connect to PostgreSQL and print schema information."""
    conn = psycopg.connect(database_url)
    cur = conn.cursor()

    # List all tables
    print("=" * 80)
    print("TABLES")
    print("=" * 80)
    cur.execute("""
        SELECT table_schema, table_name, table_type
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    tables = cur.fetchall()
    for _schema, name, ttype in tables:
        print(f"  {name:30s} ({ttype})")

    print(f"\nTotal tables: {len(tables)}")

    # List all columns per table
    print("\n" + "=" * 80)
    print("COLUMNS")
    print("=" * 80)
    cur.execute("""
        SELECT
            c.table_name,
            c.column_name,
            c.data_type,
            c.is_nullable,
            c.column_default
        FROM information_schema.columns c
        WHERE c.table_schema = 'public'
        ORDER BY c.table_name, c.ordinal_position;
    """)
    columns = cur.fetchall()

    current_table = None
    for table_name, col_name, data_type, nullable, default in columns:
        if table_name != current_table:
            current_table = table_name
            print(f"\n  [{table_name}]")
        default_str = f" DEFAULT {default}" if default else ""
        print(f"    {col_name:30s} {data_type:20s} NULL={nullable}{default_str}")

    print(f"\nTotal columns: {len(columns)}")

    # List all indexes
    print("\n" + "=" * 80)
    print("INDEXES")
    print("=" * 80)
    cur.execute("""
        SELECT
            i.relname AS index_name,
            t.relname AS table_name,
            am.amname AS index_type,
            ix.indisunique AS is_unique
        FROM pg_class t
        JOIN pg_index ix ON t.oid = ix.indrelid
        JOIN pg_class i ON i.oid = ix.indexrelid
        JOIN pg_am am ON i.relam = am.oid
        WHERE t.relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
        ORDER BY t.relname, i.relname;
    """)
    indexes = cur.fetchall()
    for idx_name, tbl_name, idx_type, is_unique in indexes:
        unique_str = "UNIQUE " if is_unique else ""
        print(f"  {tbl_name:30s} {unique_str}{idx_type:10s} {idx_name}")

    print(f"\nTotal indexes: {len(indexes)}")

    # List sequences
    print("\n" + "=" * 80)
    print("SEQUENCES")
    print("=" * 80)
    cur.execute("""
        SELECT sequence_name
        FROM information_schema.sequences
        WHERE sequence_schema = 'public'
        ORDER BY sequence_name;
    """)
    sequences = cur.fetchall()
    for (seq_name,) in sequences:
        print(f"  {seq_name}")

    print(f"\nTotal sequences: {len(sequences)}")

    # List foreign keys
    print("\n" + "=" * 80)
    print("FOREIGN KEYS")
    print("=" * 80)
    cur.execute("""
        SELECT
            tc.constraint_name,
            tc.table_name,
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage ccu
            ON ccu.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema = 'public'
        ORDER BY tc.table_name;
    """)
    fkeys = cur.fetchall()
    for _constraint, table, column, foreign_table, foreign_column in fkeys:
        print(f"  {table}.{column} -> {foreign_table}.{foreign_column}")

    if not fkeys:
        print("  (none found)")

    conn.close()


def main():
    parser = argparse.ArgumentParser(description="Inspect PostgreSQL schema")
    parser.add_argument(
        "--database-url",
        default="postgresql://paradox:changeme@localhost:5432/paradox",
        help="PostgreSQL connection URL",
    )
    args = parser.parse_args()

    try:
        inspect_schema(args.database_url)
    except psycopg.OperationalError as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
