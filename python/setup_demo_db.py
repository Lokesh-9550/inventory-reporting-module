"""
setup_demo_db.py
Creates and seeds a local SQLite database (inventory_demo.db) mirroring
sql/schema.sql, so the reporting module can be run and tested without
setting up a MySQL server.

Usage:
    python setup_demo_db.py
"""

import sqlite3
import os

DB_PATH = os.environ.get("SQLITE_DB_PATH", "inventory_demo.db")

SCHEMA = """
DROP TABLE IF EXISTS stock_movements;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS warehouses;

CREATE TABLE warehouses (
    warehouse_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    warehouse_name TEXT NOT NULL UNIQUE,
    city           TEXT
);

CREATE TABLE products (
    product_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    product_code   TEXT NOT NULL UNIQUE,
    product_name   TEXT NOT NULL,
    category       TEXT,
    unit_price     REAL NOT NULL,
    reorder_level  INTEGER NOT NULL DEFAULT 10
);

CREATE TABLE stock_movements (
    movement_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id      INTEGER NOT NULL,
    warehouse_id    INTEGER NOT NULL,
    movement_type   TEXT NOT NULL CHECK (movement_type IN ('IN', 'OUT')),
    quantity        INTEGER NOT NULL,
    movement_date   TEXT NOT NULL,
    reference_note  TEXT,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id)
);
"""

SEED = """
INSERT INTO warehouses (warehouse_name, city) VALUES
('Central Warehouse', 'Nellore'),
('North Hub', 'Hyderabad'),
('South Hub', 'Chennai');

INSERT INTO products (product_code, product_name, category, unit_price, reorder_level) VALUES
('P-1001', 'Wireless Mouse', 'Electronics', 450.00, 20),
('P-1002', 'Mechanical Keyboard', 'Electronics', 2200.00, 15),
('P-1003', 'USB-C Cable 1m', 'Accessories', 150.00, 50),
('P-1004', 'Laptop Stand', 'Accessories', 900.00, 10),
('P-1005', '27-inch Monitor', 'Electronics', 14500.00, 5);

INSERT INTO stock_movements (product_id, warehouse_id, movement_type, quantity, movement_date, reference_note) VALUES
(1, 1, 'IN',  100, '2026-01-05', 'Initial stock'),
(1, 1, 'OUT', 30,  '2026-02-10', 'Bulk order #A101'),
(2, 1, 'IN',  60,  '2026-01-08', 'Initial stock'),
(2, 2, 'IN',  40,  '2026-01-15', 'Transfer-in'),
(2, 1, 'OUT', 20,  '2026-03-02', 'Retail sale batch'),
(3, 1, 'IN',  300, '2026-01-05', 'Initial stock'),
(3, 1, 'OUT', 150, '2026-02-20', 'Online orders Feb'),
(3, 3, 'IN',  100, '2026-01-20', 'Initial stock'),
(4, 2, 'IN',  50,  '2026-01-10', 'Initial stock'),
(4, 2, 'OUT', 45,  '2026-03-15', 'Corporate order'),
(5, 1, 'IN',  20,  '2026-01-12', 'Initial stock'),
(5, 1, 'OUT', 17,  '2026-02-28', 'Office setup batch'),
(5, 3, 'IN',  10,  '2026-01-25', 'Initial stock');
"""


def main():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.executescript(SCHEMA)
    cur.executescript(SEED)
    conn.commit()
    conn.close()
    print(f"Demo database created at: {DB_PATH}")


if __name__ == "__main__":
    main()
