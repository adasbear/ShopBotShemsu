-- =====================================================
-- DELIVERY BOT - PostgreSQL Schema for Supabase
-- =====================================================
-- Run this entire file in Supabase Dashboard > SQL Editor
-- Tables must be created in this order (FK dependencies)
-- =====================================================


-- =====================================================
-- TABLE 1: users
-- Stores registered bot users
-- =====================================================
CREATE TABLE IF NOT EXISTS users (
    user_id    BIGINT PRIMARY KEY,          -- Telegram user ID
    full_name  TEXT NOT NULL,                -- User's registered name
    username   TEXT,                         -- Telegram @username (nullable)
    banned     BOOLEAN DEFAULT FALSE,        -- Admin can ban users
    created_at TIMESTAMPTZ DEFAULT NOW()     -- Registration timestamp
);


-- =====================================================
-- TABLE 2: menu
-- Dynamic food/drink items and their prices
-- =====================================================
CREATE TABLE IF NOT EXISTS menu (
    name  TEXT PRIMARY KEY,          -- Item name (e.g. "Burger")
    price NUMERIC(10,2) NOT NULL    -- Price in dollars (e.g. 5.99)
);


-- =====================================================
-- TABLE 3: orders
-- Every order placed by users
-- =====================================================
CREATE TABLE IF NOT EXISTS orders (
    id        BIGSERIAL PRIMARY KEY,          -- Auto-incrementing order ID
    user_id   BIGINT NOT NULL REFERENCES users(user_id),  -- Who placed it
    item      TEXT NOT NULL,                  -- Item name (matches menu.name)
    qty       INTEGER NOT NULL CHECK (qty > 0),  -- Quantity ordered
    status    TEXT NOT NULL DEFAULT 'Pending',     -- 'Pending' or 'Arrived'
    timestamp TIMESTAMPTZ DEFAULT NOW()       -- When the order was placed
);

-- Indexes for fast lookups
CREATE INDEX IF NOT EXISTS idx_orders_user_id    ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_status     ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_timestamp  ON orders(timestamp);


-- =====================================================
-- TABLE 4: feedback
-- User-submitted feedback messages
-- =====================================================
CREATE TABLE IF NOT EXISTS feedback (
    id         BIGSERIAL PRIMARY KEY,           -- Auto-incrementing feedback ID
    user_id    BIGINT NOT NULL REFERENCES users(user_id),  -- Who submitted it
    name       TEXT NOT NULL,                    -- User's display name
    msg        TEXT NOT NULL,                    -- Feedback content
    created_at TIMESTAMPTZ DEFAULT NOW()         -- Submission timestamp
);


-- =====================================================
-- SEED DATA: Default menu items
-- Only inserts if menu table is empty
-- =====================================================
INSERT INTO menu (name, price) VALUES
    ('Burger', 5.0),
    ('Pizza',  8.0),
    ('Fries',  2.5),
    ('Coke',   1.5)
ON CONFLICT (name) DO NOTHING;
