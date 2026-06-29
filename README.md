# Custom Inventory Reporting Module

A small reporting module simulating an enterprise inventory system —
products, warehouses, and stock movements — with relational data modeling
and optimized SQL reporting queries.

## Features

- **Stock summary**: current stock per product, per warehouse (derived
  from an append-only movement ledger, not a stored balance)
- **Movement history**: full IN/OUT transaction history for any product
- **Low-stock alert**: products below their configured reorder level
- Works with **zero setup** against a local SQLite demo DB, or against
  **MySQL** for a production-style setup (same schema, same queries)

## Tech Stack

- SQL (MySQL 8 schema in `sql/schema.sql`)
- Python 3 (`sqlite3` / `mysql-connector-python`)
- `argparse` for a simple CLI

## Project Structure

```
inventory-reporting-module/
├── sql/
│   └── schema.sql            # MySQL schema, seed data, commented report queries
├── python/
│   ├── db.py                 # Connection helper (SQLite or MySQL)
│   ├── setup_demo_db.py      # Builds a local SQLite demo DB (no setup needed)
│   ├── inventory_report.py   # CLI: stock-summary / movement-history / low-stock
│   └── requirements.txt
└── DATA_MODEL.md             # Data model & query logic write-up (handoff doc)
```

## Quickstart (SQLite demo — no setup required)

```bash
cd python
python3 setup_demo_db.py
python3 inventory_report.py stock-summary
python3 inventory_report.py movement-history --product-code P-1001
python3 inventory_report.py low-stock
```

Sample output:

```
=== Current Stock Summary (per product / per warehouse) ===
product_code | product_name        | warehouse_name    | current_stock
----------------------------------------------------------------------
P-1001       | Wireless Mouse      | Central Warehouse | 70
P-1002       | Mechanical Keyboard | Central Warehouse | 40
...
```

## Production Setup (MySQL)

```bash
mysql -u root -p < sql/schema.sql

export INVENTORY_DB_BACKEND=mysql
export DB_HOST=localhost
export DB_USER=root
export DB_PASSWORD=your_password
export DB_NAME=inventory_reporting_db

pip install -r python/requirements.txt
python3 python/inventory_report.py stock-summary
```

## Data Model

See [`DATA_MODEL.md`](DATA_MODEL.md) for full details on the entity
relationships, the derived current-stock calculation, and extension ideas
(FIFO costing, suppliers, scheduled alerts).

## Notes

This was built as a fresher portfolio project to demonstrate relational
data modeling, optimized SQL (aggregate `CASE`/`SUM`, multi-table `JOIN`s),
and clear documentation practices referenced on my resume.
