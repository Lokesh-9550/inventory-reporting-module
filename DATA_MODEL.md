# Data Model & Query Logic — Custom Inventory Reporting Module

This document describes the relational data model and reporting logic,
written to support handoff/onboarding, similar to enterprise specification
documentation.

## Entity Overview

| Table             | Purpose                                                   |
|-------------------|-------------------------------------------------------------|
| `warehouses`      | Master list of physical storage locations                 |
| `products`        | Master list of items tracked, with reorder thresholds      |
| `stock_movements` | Transaction log of all stock IN (received) / OUT (issued)  |

## Relationships

- `stock_movements.product_id` → `products.product_id` (many-to-one)
- `stock_movements.warehouse_id` → `warehouses.warehouse_id` (many-to-one)
- Stock movements form an append-only ledger; **current stock is never
  stored directly** — it is always derived by summing movements. This
  avoids data drift between a stored "balance" field and the actual
  transaction history.

## Derived Metric: Current Stock

```
current_stock(product, warehouse) = SUM(quantity WHERE type = 'IN')
                                   - SUM(quantity WHERE type = 'OUT')
```

Implemented via a single `GROUP BY product_id, warehouse_id` query with a
`CASE` expression inside `SUM()` (see `stock_summary()` in
`inventory_report.py`).

## Reports Provided

1. **Stock Summary** — current stock per product, broken down per
   warehouse. Answers: "how much of X do we have, and where?"
2. **Movement History** — chronological ledger of all IN/OUT transactions
   for one product. Answers: "what happened to stock of X over time?"
3. **Low Stock Alert** — products whose *total* stock (summed across all
   warehouses) has fallen below their configured `reorder_level`.
   Answers: "what do we need to reorder?"

## Why SQLite for the demo, MySQL for production

The reporting logic is pure SQL and works unchanged on both backends — the
only difference is the connection (see `db.py`) and the parameter
placeholder style (`?` vs `%s`), which `inventory_report.py` already
handles via `get_backend()`. This was a deliberate design choice so the
module can be exercised and demoed with zero setup, while still matching
the production MySQL schema in `sql/schema.sql` field-for-field.

## Extension Points

- Add a `unit_cost_at_movement` column to `stock_movements` to support
  weighted-average or FIFO inventory valuation.
- Add a `suppliers` table and link it to `IN` movements for purchase
  traceability.
- Add a scheduled job (cron + this script) to email the low-stock report
  daily.
