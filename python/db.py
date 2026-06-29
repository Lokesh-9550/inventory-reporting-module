"""
db.py
Database connection helper for the Inventory Reporting Module.

Supports two backends:
  - MySQL (production target, matches sql/schema.sql)
  - SQLite (zero-setup local/demo mode, same schema, for quick testing)

Set INVENTORY_DB_BACKEND=mysql|sqlite (default: sqlite) to choose.
"""

import os
import sqlite3


def get_connection():
    backend = os.environ.get("INVENTORY_DB_BACKEND", "sqlite").lower()

    if backend == "mysql":
        import mysql.connector  # pip install mysql-connector-python
        return mysql.connector.connect(
            host=os.environ.get("DB_HOST", "localhost"),
            user=os.environ.get("DB_USER", "root"),
            password=os.environ.get("DB_PASSWORD", ""),
            database=os.environ.get("DB_NAME", "inventory_reporting_db"),
        )

    # Default: SQLite demo mode
    db_path = os.environ.get("SQLITE_DB_PATH", "inventory_demo.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def get_backend():
    return os.environ.get("INVENTORY_DB_BACKEND", "sqlite").lower()
