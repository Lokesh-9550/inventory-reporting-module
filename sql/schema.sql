-- Custom Inventory Reporting Module
-- Schema: products, warehouses, stock_movements
-- Author: Puttam Lokesh

DROP DATABASE IF EXISTS inventory_reporting_db;
CREATE DATABASE inventory_reporting_db;
USE inventory_reporting_db;

CREATE TABLE warehouses (
    warehouse_id   INT AUTO_INCREMENT PRIMARY KEY,
    warehouse_name VARCHAR(100) NOT NULL UNIQUE,
    city           VARCHAR(100)
);

CREATE TABLE products (
    product_id     INT AUTO_INCREMENT PRIMARY KEY,
    product_code   VARCHAR(20) NOT NULL UNIQUE,
    product_name   VARCHAR(150) NOT NULL,
    category       VARCHAR(50),
    unit_price     DECIMAL(10,2) NOT NULL,
    reorder_level  INT NOT NULL DEFAULT 10
);

-- movement_type: IN (stock received), OUT (stock issued/sold)
CREATE TABLE stock_movements (
    movement_id     INT AUTO_INCREMENT PRIMARY KEY,
    product_id      INT NOT NULL,
    warehouse_id    INT NOT NULL,
    movement_type   ENUM('IN', 'OUT') NOT NULL,
    quantity        INT NOT NULL,
    movement_date   DATE NOT NULL,
    reference_note  VARCHAR(200),
    CONSTRAINT fk_movement_product
        FOREIGN KEY (product_id) REFERENCES products(product_id),
    CONSTRAINT fk_movement_warehouse
        FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id)
);

-- Seed data
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

-- ===========================================================
-- Reporting Queries
-- ===========================================================

-- 1. Current stock summary per product per warehouse
-- (SUM of IN minus SUM of OUT)
-- SELECT p.product_code, p.product_name, w.warehouse_name,
--        COALESCE(SUM(CASE WHEN sm.movement_type = 'IN' THEN sm.quantity ELSE 0 END), 0)
--      - COALESCE(SUM(CASE WHEN sm.movement_type = 'OUT' THEN sm.quantity ELSE 0 END), 0) AS current_stock
-- FROM products p
-- JOIN stock_movements sm ON p.product_id = sm.product_id
-- JOIN warehouses w ON sm.warehouse_id = w.warehouse_id
-- GROUP BY p.product_id, w.warehouse_id
-- ORDER BY p.product_code, w.warehouse_name;

-- 2. Movement history for a specific product
-- SELECT sm.movement_date, w.warehouse_name, sm.movement_type, sm.quantity, sm.reference_note
-- FROM stock_movements sm
-- JOIN warehouses w ON sm.warehouse_id = w.warehouse_id
-- WHERE sm.product_id = 1
-- ORDER BY sm.movement_date;

-- 3. Products below reorder level (across all warehouses combined)
-- SELECT p.product_code, p.product_name, p.reorder_level,
--        COALESCE(SUM(CASE WHEN sm.movement_type = 'IN' THEN sm.quantity ELSE -sm.quantity END), 0) AS total_stock
-- FROM products p
-- LEFT JOIN stock_movements sm ON p.product_id = sm.product_id
-- GROUP BY p.product_id
-- HAVING total_stock < p.reorder_level;
