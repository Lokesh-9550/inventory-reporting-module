"""
inventory_report.py
Custom Inventory Reporting Module.

Generates:
  1. Current stock summary per product per warehouse
  2. Movement history for a given product
  3. Low-stock alert report (products below reorder level)

Works against either SQLite (default, zero-setup) or MySQL
(set INVENTORY_DB_BACKEND=mysql + DB_HOST/DB_USER/DB_PASSWORD/DB_NAME).

Usage:
    python inventory_report.py stock-summary
    python inventory_report.py movement-history --product-code P-1001
    python inventory_report.py low-stock
"""

import argparse
from db import get_connection, get_backend


def run_query(conn, sql, params=()):
    cur = conn.cursor()
    cur.execute(sql, params)
    columns = [desc[0] for desc in cur.description]
    rows = cur.fetchall()
    return columns, rows


def print_table(columns, rows):
    if not rows:
        print("No data found.")
        return
    widths = [max(len(str(col)), *(len(str(row[i])) for row in rows)) for i, col in enumerate(columns)]
    header = " | ".join(str(col).ljust(widths[i]) for i, col in enumerate(columns))
    print(header)
    print("-" * len(header))
    for row in rows:
        print(" | ".join(str(row[i]).ljust(widths[i]) for i in range(len(columns))))


def stock_summary(conn):
    """Current stock per product per warehouse = SUM(IN) - SUM(OUT)."""
    sql = """
        SELECT p.product_code,
               p.product_name,
               w.warehouse_name,
               COALESCE(SUM(CASE WHEN sm.movement_type = 'IN' THEN sm.quantity ELSE 0 END), 0)
             - COALESCE(SUM(CASE WHEN sm.movement_type = 'OUT' THEN sm.quantity ELSE 0 END), 0) AS current_stock
        FROM products p
        JOIN stock_movements sm ON p.product_id = sm.product_id
        JOIN warehouses w ON sm.warehouse_id = w.warehouse_id
        GROUP BY p.product_id, w.warehouse_id
        ORDER BY p.product_code, w.warehouse_name
    """
    columns, rows = run_query(conn, sql)
    print("\n=== Current Stock Summary (per product / per warehouse) ===")
    print_table(columns, rows)


def movement_history(conn, product_code):
    """Movement history for a specific product, by product_code."""
    sql = """
        SELECT sm.movement_date, w.warehouse_name, sm.movement_type, sm.quantity, sm.reference_note
        FROM stock_movements sm
        JOIN warehouses w ON sm.warehouse_id = w.warehouse_id
        JOIN products p ON sm.product_id = p.product_id
        WHERE p.product_code = ?
        ORDER BY sm.movement_date
    """
    if get_backend() == "mysql":
        sql = sql.replace("?", "%s")

    columns, rows = run_query(conn, sql, (product_code,))
    print(f"\n=== Movement History for {product_code} ===")
    print_table(columns, rows)


def low_stock(conn):
    """Products whose total stock (across all warehouses) is below reorder level."""
    sql = """
        SELECT p.product_code,
               p.product_name,
               p.reorder_level,
               COALESCE(SUM(CASE WHEN sm.movement_type = 'IN' THEN sm.quantity ELSE -sm.quantity END), 0) AS total_stock
        FROM products p
        LEFT JOIN stock_movements sm ON p.product_id = sm.product_id
        GROUP BY p.product_id
        HAVING total_stock < p.reorder_level
        ORDER BY total_stock ASC
    """
    columns, rows = run_query(conn, sql)
    print("\n=== Low Stock Alert (below reorder level) ===")
    print_table(columns, rows)


def main():
    parser = argparse.ArgumentParser(description="Custom Inventory Reporting Module")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("stock-summary", help="Current stock per product per warehouse")

    history_parser = subparsers.add_parser("movement-history", help="Movement history for a product")
    history_parser.add_argument("--product-code", required=True)

    subparsers.add_parser("low-stock", help="Products below reorder level")

    args = parser.parse_args()
    conn = get_connection()

    try:
        if args.command == "stock-summary":
            stock_summary(conn)
        elif args.command == "movement-history":
            movement_history(conn, args.product_code)
        elif args.command == "low-stock":
            low_stock(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
