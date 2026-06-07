-- Run this in Supabase Dashboard > SQL Editor to add the notifications table
-- (login_otps and sessions already exist)

-- 14. notifications — push notification history
CREATE TABLE IF NOT EXISTS notifications (
  id SERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  order_group TEXT,
  read BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);

-- 15. daily_menu_limit — daily stock limits per menu item
CREATE TABLE IF NOT EXISTS daily_menu_limit (
  name TEXT PRIMARY KEY,
  max_qty INTEGER NOT NULL DEFAULT 0,
  remaining INTEGER NOT NULL DEFAULT 0,
  date DATE NOT NULL DEFAULT CURRENT_DATE,
  locked BOOLEAN DEFAULT FALSE,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
