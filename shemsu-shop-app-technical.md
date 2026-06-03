# Shemsu Shop — Android App Technical Specification

---

## 1. Connection Credentials

### Supabase
```
SUPABASE_URL = https://[your-project].supabase.co
SUPABASE_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... (anon public key)
SUPABASE_SERVICE_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... (service_role key, server-side only)
```

### Telegram Bot
```
BOT_TOKEN = 8956788017:AAGN-OW6t985HCbGNITJd2t8bkX5CXK6Etw
```

### Admin
```
ADMIN_USERNAME = PPopa054
ADMIN_USER_ID = 7041035485
```

### Backend API (Flask, hosted on Render)
```
API_BASE_URL = https://shopbotshemsu-1.onrender.com
```

---

## 2. Complete SQL — All Tables

Run this entire block in Supabase SQL Editor **once**.

```sql
-- ============================================
-- 1. users
-- ============================================
CREATE TABLE IF NOT EXISTS users (
  user_id BIGINT PRIMARY KEY,
  full_name TEXT NOT NULL,
  username TEXT,
  banned BOOLEAN DEFAULT FALSE,
  phone TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 2. menu
-- ============================================
CREATE TABLE IF NOT EXISTS menu (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  price NUMERIC NOT NULL DEFAULT 0,
  parent TEXT REFERENCES menu(name) ON DELETE CASCADE,
  available BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 3. orders
-- ============================================
CREATE TABLE IF NOT EXISTS orders (
  id SERIAL PRIMARY KEY,
  user_id BIGINT REFERENCES users(user_id),
  item TEXT NOT NULL,
  qty INTEGER NOT NULL,
  status TEXT DEFAULT 'Pending',
  order_group TEXT,
  timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 4. order_comments
-- ============================================
CREATE TABLE IF NOT EXISTS order_comments (
  id SERIAL PRIMARY KEY,
  order_group TEXT UNIQUE NOT NULL,
  comment TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 5. order_payments
-- ============================================
CREATE TABLE IF NOT EXISTS order_payments (
  order_group TEXT PRIMARY KEY,
  payment_info TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 6. order_decline_reasons
-- ============================================
CREATE TABLE IF NOT EXISTS order_decline_reasons (
  order_group TEXT PRIMARY KEY,
  reason TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 7. feedback
-- ============================================
CREATE TABLE IF NOT EXISTS feedback (
  id SERIAL PRIMARY KEY,
  user_id BIGINT,
  name TEXT,
  msg TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 8. debt_allow_list
-- ============================================
CREATE TABLE IF NOT EXISTS debt_allow_list (
  id SERIAL PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  added_by BIGINT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 9. debts
-- ============================================
CREATE TABLE IF NOT EXISTS debts (
  id SERIAL PRIMARY KEY,
  username TEXT NOT NULL,
  user_id BIGINT,
  full_name TEXT,
  amount NUMERIC NOT NULL,
  description TEXT DEFAULT '',
  order_group TEXT,
  status TEXT DEFAULT 'active',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  paid_at TIMESTAMPTZ
);

-- ============================================
-- 10. debt_payments
-- ============================================
CREATE TABLE IF NOT EXISTS debt_payments (
  id SERIAL PRIMARY KEY,
  username TEXT NOT NULL,
  user_id BIGINT,
  amount NUMERIC NOT NULL,
  payment_info TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 11. payment_accounts
-- ============================================
CREATE TABLE IF NOT EXISTS payment_accounts (
  id SERIAL PRIMARY KEY,
  bank_name TEXT NOT NULL,
  number TEXT NOT NULL,
  holder_name TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 12. login_otps (new — for app auth)
-- ============================================
CREATE TABLE IF NOT EXISTS login_otps (
  id SERIAL PRIMARY KEY,
  username TEXT NOT NULL,
  user_id BIGINT,
  otp TEXT NOT NULL,
  expires_at TIMESTAMPTZ NOT NULL,
  used BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 13. notifications (new — for push)
-- ============================================
CREATE TABLE IF NOT EXISTS notifications (
  id SERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  order_group TEXT,
  read BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- Default payment accounts seed
-- ============================================
INSERT INTO payment_accounts (bank_name, number, holder_name)
SELECT * FROM (VALUES
  ('CBE', '1000404793199', 'Alazar'),
  ('Abyssinia', '207710668', 'Alazar'),
  ('Awash', '013201733496400', 'Alazar'),
  ('Telebirr', '0907319664', 'Alazar')
) AS t
WHERE NOT EXISTS (SELECT 1 FROM payment_accounts);
```

---

## 3. Database Indexes (Performance)

```sql
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_order_group ON orders(order_group);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_timestamp ON orders(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_order_comments_order_group ON order_comments(order_group);
CREATE INDEX IF NOT EXISTS idx_order_payments_order_group ON order_payments(order_group);
CREATE INDEX IF NOT EXISTS idx_debts_username ON debts(username);
CREATE INDEX IF NOT EXISTS idx_debts_status ON debts(status);
CREATE INDEX IF NOT EXISTS idx_debt_allow_list_username ON debt_allow_list(username);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_menu_parent ON menu(parent);
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(read);
CREATE INDEX IF NOT EXISTS idx_login_otps_username ON login_otps(username);
CREATE INDEX IF NOT EXISTS idx_login_otps_otp ON login_otps(otp);
```

---

## 4. Row-Level Security (RLS) Policies

Enable RLS on every table. The anon key can **read** public data and **write** its own data only.

```sql
-- users: user can read/update own row
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
CREATE POLICY users_select_own ON users FOR SELECT USING (user_id = current_setting('app.user_id')::BIGINT OR current_setting('app.is_admin')::BOOLEAN);
CREATE POLICY users_update_own ON users FOR UPDATE USING (user_id = current_setting('app.user_id')::BIGINT);

-- menu: public read
ALTER TABLE menu ENABLE ROW LEVEL SECURITY;
CREATE POLICY menu_select_all ON menu FOR SELECT USING (true);

-- orders: user reads own, inserts own
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
CREATE POLICY orders_select_own ON orders FOR SELECT USING (user_id = current_setting('app.user_id')::BIGINT);
CREATE POLICY orders_insert_own ON orders FOR INSERT WITH CHECK (user_id = current_setting('app.user_id')::BIGINT);
CREATE POLICY orders_update_own ON orders FOR UPDATE USING (user_id = current_setting('app.user_id')::BIGINT);

-- order_comments: same
ALTER TABLE order_comments ENABLE ROW LEVEL SECURITY;
CREATE POLICY order_comments_select ON order_comments FOR SELECT USING (true);

-- order_payments: same
ALTER TABLE order_payments ENABLE ROW LEVEL SECURITY;
CREATE POLICY order_payments_select_own ON order_payments FOR SELECT USING (true);

-- order_decline_reasons: same
ALTER TABLE order_decline_reasons ENABLE ROW LEVEL SECURITY;
CREATE POLICY order_decline_reasons_select ON order_decline_reasons FOR SELECT USING (true);

-- debts: user reads own
ALTER TABLE debts ENABLE ROW LEVEL SECURITY;
CREATE POLICY debts_select_own ON debts FOR SELECT USING (username = current_setting('app.username')::TEXT);

-- debt_payments: user inserts own
ALTER TABLE debt_payments ENABLE ROW LEVEL SECURITY;
CREATE POLICY debt_payments_select_own ON debt_payments FOR SELECT USING (username = current_setting('app.username')::TEXT);
CREATE POLICY debt_payments_insert_own ON debt_payments FOR INSERT WITH CHECK (username = current_setting('app.username')::TEXT);

-- debt_allow_list: public read
ALTER TABLE debt_allow_list ENABLE ROW LEVEL SECURITY;
CREATE POLICY debt_allow_list_select ON debt_allow_list FOR SELECT USING (true);

-- payment_accounts: public read
ALTER TABLE payment_accounts ENABLE ROW LEVEL SECURITY;
CREATE POLICY payment_accounts_select ON payment_accounts FOR SELECT USING (true);

-- feedback: user inserts own
ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;
CREATE POLICY feedback_insert_own ON feedback FOR INSERT WITH CHECK (user_id = current_setting('app.user_id')::BIGINT);

-- notifications: user reads own, updates read status
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
CREATE POLICY notifications_select_own ON notifications FOR SELECT USING (user_id = current_setting('app.user_id')::BIGINT);
CREATE POLICY notifications_update_own ON notifications FOR UPDATE USING (user_id = current_setting('app.user_id')::BIGINT);

-- login_otps: insert/select via service_role only (not exposed to anon key)
```

---

## 5. Complete API Endpoints

The backend API runs as a Flask service. All endpoints return JSON.

### 5.1 Auth

#### `POST /api/auth/request-otp`
```json
// Request
{ "username": "@PPopa054" }

// Response 200
{ "success": true, "message": "OTP sent to your Telegram" }

// Response 404
{ "success": false, "error": "Username not found in system" }

// Response 429
{ "success": false, "error": "Too many requests. Try again in 5 minutes." }
```
**SQL executed:**
```sql
-- Check if user exists
SELECT user_id FROM users WHERE username = 'PPopa054';
-- Delete old OTPs for this user
DELETE FROM login_otps WHERE username = 'PPopa054' AND used = FALSE;
-- Insert new OTP
INSERT INTO login_otps (username, user_id, otp, expires_at)
VALUES ('PPopa054', 123456789, '483921', NOW() + INTERVAL '5 minutes');
```
**Bot action:** sends `"Your Shemsu Shop login code: 483921\n\nExpires in 5 minutes."` to the Telegram user.

---

#### `POST /api/auth/verify-otp`
```json
// Request
{ "username": "@PPopa054", "otp": "483921" }

// Response 200
{ "success": true, "session_token": "a1b2c3d4-e5f6-7890-abcd-ef1234567890" }

// Response 401
{ "success": false, "error": "Invalid or expired OTP" }
```
**SQL executed:**
```sql
SELECT * FROM login_otps
WHERE username = 'PPopa054'
  AND otp = '483921'
  AND used = FALSE
  AND expires_at > NOW();
-- If found:
UPDATE login_otps SET used = TRUE WHERE id = X;
```

---

#### `GET /api/auth/session?token=UUID`
```json
// Response 200
{ "user_id": 123456789, "username": "PPopa054", "full_name": "Adil" }

// Response 401
{ "success": false, "error": "Invalid session" }
```

---

### 5.2 User Profile

#### `GET /api/user/profile?user_id=123456789`
```sql
SELECT user_id, full_name, username, phone, banned, created_at
FROM users WHERE user_id = 123456789;
```
```json
{ "user_id": 123456789, "full_name": "Adil", "username": "PPopa054", "banned": false, "created_at": "2025-01-15T..." }
```

#### `PUT /api/user/profile`
```json
// Request
{ "user_id": 123456789, "full_name": "Adil New" }
```
```sql
UPDATE users SET full_name = 'Adil New' WHERE user_id = 123456789;
```
```json
{ "success": true }
```

---

### 5.3 Menu

#### `GET /api/menu`
```sql
SELECT id, name, price, parent, available
FROM menu WHERE available = TRUE
ORDER BY parent NULLS FIRST, name;
```
Returns flat list. The app builds the category tree in memory.
```json
[
  { "id": 1, "name": "Breakfast", "price": 0.0, "parent": null, "available": true },
  { "id": 2, "name": "Fetira", "price": 160.0, "parent": "Breakfast", "available": true },
  { "id": 3, "name": "Burger", "price": 200.0, "parent": null, "available": true }
]
```

#### `GET /api/menu?parent=Breakfast`
```sql
SELECT id, name, price, parent, available
FROM menu WHERE parent = 'Breakfast' AND available = TRUE;
```

---

### 5.4 Orders

#### `POST /api/orders` — Place an order
```json
{
  "user_id": 123456789,
  "username": "PPopa054",
  "full_name": "Adil",
  "items": [
    { "item": "Fetira", "qty": 4, "price": 160.0 },
    { "item": "Tea", "qty": 2, "price": 50.0 }
  ],
  "payment_method": "pay",           // or "debt"
  "payment_account_id": 4,           // null if debt
  "confirmation": "Transfer of 740.00 ETB to Telebirr 0907319664 successful. Ref: TRF-12345",
  "comment": "No sugar please"       // optional
}
```

**SQL transaction:**
```sql
-- 1. Generate order_group
-- Format: {user_id}_{epoch_ms}
-- e.g., "123456789_1717200000123"

-- 2. Insert each item
INSERT INTO orders (user_id, item, qty, status, order_group, timestamp)
VALUES (123456789, 'Fetira', 4, 'Pending', '123456789_1717200000123', NOW()),
       (123456789, 'Tea', 2, 'Pending', '123456789_1717200000123', NOW());

-- 3. If payment method = pay:
INSERT INTO order_payments (order_group, payment_info)
VALUES ('123456789_1717200000123',
        'Telebirr - 0907319664 (Alazar)\nConfirmation: Transfer of 740.00 ETB to Telebirr 0907319664 successful. Ref: TRF-12345');

-- 4. If payment method = debt:
-- (order placed on debt, no payment record yet)

-- 5. Save comment if provided:
INSERT INTO order_comments (order_group, comment)
VALUES ('123456789_1717200000123', 'No sugar please');
```

**Response:**
```json
{
  "success": true,
  "order_group": "123456789_1717200000123",
  "total": 740.0,
  "payment_method": "pay",
  "status": "Pending"
}
```

**Backend then notifies admin via Telegram bot:**
```
NEW ORDER FROM: Adil

4x Fetira (Birr 640.00)
2x Tea (Birr 100.00)

TOTAL: Birr 740.00

Payment:
Telebirr - 0907319664 (Alazar)
Confirmation: Transfer of 740.00 ETB to Telebirr 0907319664 successful. Ref: TRF-12345

Comment: No sugar please
```

---

#### `GET /api/orders?user_id=123456789`
```sql
SELECT id, item, qty, status, order_group, timestamp
FROM orders
WHERE user_id = 123456789
ORDER BY timestamp DESC
LIMIT 50;
```
**App groups by `order_group` in code.**

---

#### `GET /api/orders/group/{order_group}` — Full order detail
```sql
-- Items
SELECT id, item, qty, status, timestamp
FROM orders WHERE order_group = '123456789_1717200000123';

-- Payment
SELECT payment_info FROM order_payments WHERE order_group = '123456789_1717200000123';

-- Comment
SELECT comment FROM order_comments WHERE order_group = '123456789_1717200000123';

-- Decline reason (if cancelled)
SELECT reason FROM order_decline_reasons WHERE order_group = '123456789_1717200000123';
```
```json
{
  "order_group": "123456789_1717200000123",
  "items": [
    { "id": 1, "item": "Fetira", "qty": 4, "status": "Pending" },
    { "id": 2, "item": "Tea", "qty": 2, "status": "Pending" }
  ],
  "status": "Pending",
  "total": 740.0,
  "payment": "Telebirr - 0907319664 (Alazar)\nConfirmation: ...",
  "comment": "No sugar please",
  "decline_reason": null,
  "created_at": "2025-06-01T12:00:00Z"
}
```

---

#### `PUT /api/orders/{order_group}/items` — Edit quantities
```json
{
  "items": [
    { "id": 1, "qty": 5 },
    { "id": 2, "qty": 1 }
  ]
}
```
```sql
UPDATE orders SET qty = 5 WHERE id = 1 AND order_group = '...' AND status = 'Pending';
UPDATE orders SET qty = 1 WHERE id = 2 AND order_group = '...' AND status = 'Pending';
```
**Backend checks:** 6PM UTC rule — if `timestamp` is today and current UTC time >= 18:00, reject.
```sql
SELECT timestamp FROM orders WHERE order_group = '...' LIMIT 1;
-- In code: if same day AND current UTC hour >= 18, return 403
```

---

#### `DELETE /api/orders/{order_group}` — Cancel order
```sql
UPDATE orders SET status = 'Cancelled'
WHERE order_group = '...' AND status = 'Pending';
```
**Same 6PM UTC check.** Notifies admin: `"Order #... cancelled by user"`.

---

### 5.5 Debts

#### `GET /api/debts?username=PPopa054`
```sql
SELECT id, username, full_name, amount, description, order_group, status, created_at, paid_at
FROM debts
WHERE username = 'PPopa054'
ORDER BY created_at DESC
LIMIT 50;
```
```json
{
  "active_total": 500.0,
  "records": [
    { "id": 1, "amount": 500.0, "description": "Order #...", "status": "active", "created_at": "..." },
    { "id": 2, "amount": 300.0, "description": "Order #...", "status": "paid", "paid_at": "..." }
  ]
}
```

#### `GET /api/debts/active-total?username=PPopa054`
```sql
SELECT COALESCE(SUM(amount), 0) AS total
FROM debts
WHERE username = 'PPopa054' AND status = 'active';
```
```json
{ "active_total": 500.0 }
```

#### `POST /api/debts/pay` — Pay debt
```json
{
  "username": "PPopa054",
  "user_id": 123456789,
  "amount": 500.0,
  "payment_account_id": 4,
  "confirmation": "Transfer of 500.00 ETB to Telebirr 0907319664 successful."
}
```
```sql
INSERT INTO debt_payments (username, user_id, amount, payment_info)
VALUES ('PPopa054', 123456789, 500.0,
        'Telebirr - 0907319664 (Alazar)\nConfirmation: Transfer of 500.00 ETB to Telebirr 0907319664 successful.');
```
**Response:**
```json
{ "success": true, "amount": 500.0 }
```
**Backend notifies admin:**
```
DEBT PAYMENT FROM: Adil (@PPopa054)

Amount: Birr 500.00

Payment:
Telebirr - 0907319664 (Alazar)
Confirmation: Transfer of 500.00 ETB to Telebirr 0907319664 successful.
```

---

### 5.6 Payment Accounts

#### `GET /api/payment-accounts`
```sql
SELECT id, bank_name, number, holder_name
FROM payment_accounts
ORDER BY bank_name;
```
```json
[
  { "id": 1, "bank_name": "CBE", "number": "1000404793199", "holder_name": "Alazar" },
  { "id": 2, "bank_name": "Abyssinia", "number": "207710668", "holder_name": "Alazar" },
  { "id": 3, "bank_name": "Awash", "number": "013201733496400", "holder_name": "Alazar" },
  { "id": 4, "bank_name": "Telebirr", "number": "0907319664", "holder_name": "Alazar" }
]
```

---

### 5.7 Debt Allow List Check

#### `GET /api/debt-allow-list/check?username=PPopa054`
```sql
SELECT id FROM debt_allow_list WHERE username = 'PPopa054' LIMIT 1;
```
```json
{ "allowed": true }
```

---

### 5.8 Feedback

#### `POST /api/feedback`
```json
{ "user_id": 123456789, "msg": "Great service!" }
```
```sql
-- Get name
SELECT full_name FROM users WHERE user_id = 123456789;
-- Insert
INSERT INTO feedback (user_id, name, msg) VALUES (123456789, 'Adil', 'Great service!');
```
```json
{ "success": true }
```

---

### 5.9 Notifications

#### `GET /api/notifications?user_id=123456789`
```sql
SELECT id, title, body, order_group, read, created_at
FROM notifications
WHERE user_id = 123456789
ORDER BY created_at DESC
LIMIT 50;
```

#### `PUT /api/notifications/{id}/read`
```sql
UPDATE notifications SET read = TRUE WHERE id = X AND user_id = 123456789;
```

---

### 5.10 Contact Admin

#### `POST /api/contact`
```json
{ "user_id": 123456789, "username": "PPopa054", "message": "I have a question about my order" }
```
**Backend sends to admin via Telegram:**
```
CONTACT FROM: Adil (@PPopa054)

I have a question about my order
```
```json
{ "success": true }
```

---

### 5.11 Help Content

#### `GET /api/help`
```json
{
  "categories": [
    {
      "title": "How to Order",
      "content": "1. Tap Menu and browse categories.\n2. Select items and quantities.\n3. Review your cart.\n4. Pay now or take on debt (if eligible).\n5. Paste your bank confirmation.\n6. Wait for admin approval."
    },
    {
      "title": "Bot Not Responding",
      "content": "Try the Refresh button or restart the app. If the issue persists, contact admin."
    },
    {
      "title": "Custom Requests",
      "content": "If you don't see what you want, use the \"Other\" option and describe your item. Admin will review it."
    },
    {
      "title": "Edit / Cancel Orders",
      "content": "You can edit quantities or cancel your order only while it's Pending AND before 6 PM UTC on the same day."
    },
    {
      "title": "Contact Admin",
      "content": "For any issues, use the Contact Admin screen or message @PPopa054 on Telegram."
    }
  ]
}
```

---

## 6. App Architecture — Screen-by-Screen Implementation

### Screen 1: Splash
| Item | Implementation |
|------|---------------|
| UI | Jetpack Compose, centered logo + CircularProgressIndicator |
| Logic | Check SharedPreferences for session_token → if exists, call `GET /api/auth/session?token=X` → valid → Home; invalid or missing → Login |
| Duration | 2s minimum, or until session check completes |

### Screen 2: Login
| Item | Implementation |
|------|---------------|
| TextField | `OutlinedTextField`, hint "Enter your Telegram username (e.g., @username)" |
| Send OTP | `Button` → `POST /api/auth/request-otp` → on success, show OTP digits field |
| OTP input | 6 individual `OutlinedTextField` (single digit each) or one masked field |
| Verify | `Button` → `POST /api/auth/verify-otp` → on success, save session_token to EncryptedSharedPreferences → navigate to Home |
| Error | `Snackbar` for "Username not found", "Invalid OTP", "OTP expired" |
| Timer | 5-min countdown on OTP, auto-resend button appears after expiry |

### Screen 3: Home (Dashboard)
| Component | Implementation |
|-----------|---------------|
| User greeting | `Text("Hi, $fullName 👋")` from profile data |
| Active debt card | `Card` with conditional visibility — if `GET /api/debts/active-total > 0`, shows "Active Debt: Birr X.XX — Pay Now →" tapping → My Debt screen |
| Quick actions | 2×2 `LazyVerticalGrid` with icons: Order Now, My Orders, My Debt, Help |
| Recent orders | `LazyColumn`, max 3 items from `GET /api/orders?user_id=X&limit=3` |
| Bottom nav | `NavigationBar` with 4 items: Home, Menu, Orders, Profile |

#### Homescreen API calls on load
```
Parallel:
  GET /api/user/profile?user_id=X
  GET /api/debts/active-total?username=Y
  GET /api/orders?user_id=X&limit=3
  GET /api/notifications?user_id=X&limit=1  (for badge)
```

### Screen 4: Menu
| Component | Implementation |
|-----------|---------------|
| Top bar | `TopAppBar` with search icon → expands search field; cart icon with badge count |
| Categories | `LazyRow` of `FilterChip`: "All" + each parent-level menu item |
| Items grid | `LazyVerticalGrid` (2 columns) — each card shows: name, price, "Add +" button |
| Category drill-down | When user taps a category chip → filter grid to show only sub-items of that parent |
| Search | `TextField` → filter items by name (client-side) |
| Other ✏️ | Special card at bottom → `Dialog` with name TextField + quantity stepper |
| Cart FAB | `FloatingActionButton` with badge count → navigates to Cart screen |

#### SQL for menu data
```sql
SELECT id, name, price, parent, available
FROM menu WHERE available = TRUE
ORDER BY parent NULLS FIRST, name;
```

### Screen 5: Item Detail / Add to Cart
| Component | Implementation |
|-----------|---------------|
| Trigger | Tap "Add +" on any sub-item (price > 0) |
| UI | `ModalBottomSheet` with: item name, price, `Row` with minus/quantity/plus, "Add to Cart" button |
| Quantity stepper | Min 1, max 99 |
| Add to Cart | Store in local `ViewModel` cart state (MutableStateFlow<List<CartItem>>) |
| Other item | Same bottom sheet but with `OutlinedTextField` for item name instead of pre-filled name |

### Screen 6: Cart
| Component | Implementation |
|-----------|---------------|
| Item rows | `LazyColumn`, each row: name, quantity stepper, line total, delete (swipe or icon) |
| Special instructions | `ExposedDropdownMenu` collapsed → expand to `OutlinedTextField` |
| Summary | Subtotal: "Birr X.XX" |
| Buttons | "Continue to Pay" (primary, full-width), "Add More Items" (text button → back to Menu) |

#### Local state (ViewModel)
```kotlin
data class CartItem(
  val name: String,
  val price: Double,
  var qty: Int,
  val isCustom: Boolean = false
)

data class CartState(
  val items: List<CartItem>,
  val comment: String = "",
  val subtotal: Double = items.sumOf { it.price * it.qty }
)
```

### Screen 7: Checkout / Payment
| Component | Implementation |
|-----------|---------------|
| Order summary | Read-only list of items + total |
| Payment methods | `RadioButton` group populated from `GET /api/payment-accounts` |
| Take on Debt | Conditional card — only shown if `GET /api/debt-allow-list/check?username=X` returns `true` |
| Confirmation step | After selecting "Pay" method → show account details in a card + `OutlinedTextField` for confirmation SMS |
| ⚠️ Warning | Red text: "Do not send screenshots — paste the text message only." |
| Submit | `Button` → `POST /api/orders` → on success → navigate to Success screen |
| Debt flow | Confirm `Dialog` → same `POST /api/orders` with `payment_method: "debt"` |

### Screen 8: Success / Order Confirmation
| Component | Implementation |
|-----------|---------------|
| Icon | Green checkmark animation (Lottie or vector) |
| Text | "Order submitted successfully and payment info is awaiting approval." |
| Order number | "Order #123456789_1717200000123" (copyable) |
| Buttons | "View My Orders" → My Orders, "Back to Home" → Home |

### Screen 9: My Orders
| Component | Implementation |
|-----------|---------------|
| Tabs | `TabRow` with "Active" and "History" |
| Active | Orders with status Pending, Accepted, Ready — sorted by newest first |
| History | Orders with status Delivered, Cancelled |
| Order card | `Card` with: truncated order_group, date, colored status badge, item count, total, paid/debt icon |
| Tap | Navigate to Order Detail screen |

#### SQL
```sql
-- All orders for user, grouped
SELECT id, item, qty, status, order_group, timestamp
FROM orders
WHERE user_id = 123456789
ORDER BY timestamp DESC
LIMIT 50;
```

### Screen 10: Order Detail
| Component | Implementation |
|-----------|---------------|
| Status timeline | Vertical stepper with: Ordered ✅ → Accepted 🟢 → Ready 🟠 → Delivered ✅ (or Cancelled ❌ with reason) |
| Items | List of item × qty = line total |
| Total | Birr X.XX |
| Payment section | If exists: show method + confirmation text from `order_payments` |
| Comment section | If exists from `order_comments` |
| Action buttons | "Edit Items" / "Cancel Order" — only if status == "Pending" AND before 6PM UTC |
| Edit items | Navigate to edit screen with quantity steppers for each item |
| Cancel | Confirmation `Dialog` → `DELETE /api/orders/{order_group}` |

#### Status timeline data
```sql
-- Get all distinct timestamps per status for this order group
SELECT DISTINCT status, timestamp FROM orders WHERE order_group = '...' ORDER BY timestamp;
-- And payment info
SELECT payment_info FROM order_payments WHERE order_group = '...';
-- And comment
SELECT comment FROM order_comments WHERE order_group = '...';
-- And decline reason
SELECT reason FROM order_decline_reasons WHERE order_group = '...';
```

### Screen 11: My Debt
| Component | Implementation |
|-----------|---------------|
| Header card | "Active Debt: Birr X.XX" with colored background (red if > 0, green if 0) |
| Debt list | Each row: description, amount, status icon + label |
| Pay Now button | Full-width primary button — only visible if active_total > 0 |
| Pay Now flow | Same as Checkout payment flow but calls `POST /api/debts/pay` |
| Empty state | "No debt records. Great job! 🎉" with confetti animation |

#### SQL
```sql
SELECT id, username, full_name, amount, description, order_group, status, created_at, paid_at
FROM debts WHERE username = 'PPopa054' ORDER BY created_at DESC;
SELECT COALESCE(SUM(amount), 0) FROM debts WHERE username = 'PPopa054' AND status = 'active';
```

### Screen 12: Help
| Component | Implementation |
|-----------|---------------|
| Category cards | `LazyColumn` of expandable `Card` — each has title + chevron, tap to expand/collapse with `animateContentSize()` |
| Content | Hardcoded in app or fetched from `GET /api/help` |
| Contact button | "Contact Admin" button at bottom → Contact Admin screen |

### Screen 13: Feedback
| Component | Implementation |
|-----------|---------------|
| Rating bar | 5 `IconButton` stars — tap to select, filled/unfilled state |
| Message field | `OutlinedTextField` multiline (minHeight 120dp) |
| Submit | `Button` → `POST /api/feedback` |
| Success | "Thanks for your feedback! 🙏" with auto-navigate back |

### Screen 14: Profile
| Component | Implementation |
|-----------|---------------|
| Avatar | Circle with user initials (e.g., "AD") |
| Name | Display + edit icon → inline edit → `PUT /api/user/profile` |
| Username | Read-only, with copy button |
| Phone | Read-only (from Telegram) |
| Notifications | `Switch` toggle (stored in `SharedPreferences`, not server) |
| Log Out | `Button` (red) → clear session → navigate to Login |

### Screen 15: Contact Admin
| Component | Implementation |
|-----------|---------------|
| Chat list | `LazyColumn` — user messages right-aligned (blue bubbles), admin replies left-aligned (gray bubbles) |
| Input | `Row` with `OutlinedTextField` + send `IconButton` |
| Send | `POST /api/contact` — stored in DB, admin responds via Telegram bot |
| Banned notice | If `user.banned == true`, show warning text with admin username link |

### Screen 16: Notifications
| Component | Implementation |
|-----------|---------------|
| List | Each row: icon, title, body, time, read/unread indicator |
| Tap | Navigate to Order Detail if `order_group` is set |
| Mark read | `PUT /api/notifications/{id}/read` on view |

---

## 7. Data Models (Kotlin)

```kotlin
// --- API Responses ---

data class User(
  val user_id: Long,
  val full_name: String,
  val username: String?,
  val phone: String?,
  val banned: Boolean,
  val created_at: String?
)

data class MenuItem(
  val id: Int,
  val name: String,
  val price: Double,
  val parent: String?,
  val available: Boolean
)

data class CartItem(
  val item: String,
  val qty: Int,
  val price: Double,
  val isCustom: Boolean = false
)

data class OrderGroup(
  val order_group: String,
  val timestamp: String?,
  val status: String,
  val items: List<OrderItem>,
  val payment: String?,
  val comment: String?,
  val decline_reason: String?,
  val total: Double = 0.0
)

data class OrderItem(
  val id: Int,
  val item: String,
  val qty: Int,
  val status: String?
)

data class Debt(
  val id: Int,
  val username: String,
  val amount: Double,
  val description: String?,
  val status: String,
  val created_at: String?,
  val paid_at: String?
)

data class PaymentAccount(
  val id: Int,
  val bank_name: String,
  val number: String,
  val holder_name: String
)

data class Notification(
  val id: Int,
  val title: String,
  val body: String,
  val order_group: String?,
  val read: Boolean,
  val created_at: String?
)

data class PlaceOrderRequest(
  val user_id: Long,
  val username: String?,
  val full_name: String?,
  val items: List<CartItem>,
  val payment_method: String,
  val payment_account_id: Int?,
  val confirmation: String?,
  val comment: String?
)

data class DebtPayRequest(
  val username: String,
  val user_id: Long,
  val amount: Double,
  val payment_account_id: Int,
  val confirmation: String
)
```

---

## 8. State Management (ViewModel Outline)

```kotlin
// --- AuthViewModel ---
class AuthViewModel : ViewModel() {
  val sessionToken: StateFlow<String?>
  val isLoggedIn: StateFlow<Boolean>
  val currentUser: StateFlow<User?>
  fun requestOtp(username: String)
  fun verifyOtp(username: String, otp: String)
  fun logout()
}

// --- MenuViewModel ---
class MenuViewModel : ViewModel() {
  val allItems: StateFlow<List<MenuItem>>
  val categories: StateFlow<List<String>>
  val selectedCategory: StateFlow<String?>
  val searchQuery: StateFlow<String>
  val filteredItems: StateFlow<List<MenuItem>>
  fun loadMenu()
  fun selectCategory(category: String?)
  fun search(query: String)
}

// --- CartViewModel ---
class CartViewModel : ViewModel() {
  val items: StateFlow<List<CartItem>>
  val subtotal: StateFlow<Double>
  val comment: StateFlow<String>
  val itemCount: StateFlow<Int>   // for badge
  fun addItem(item: CartItem)
  fun removeItem(name: String)
  fun updateQty(name: String, qty: Int)
  fun setComment(text: String)
  fun clearCart()
}

// --- OrdersViewModel ---
class OrdersViewModel : ViewModel() {
  val activeOrders: StateFlow<List<OrderGroup>>
  val historyOrders: StateFlow<List<OrderGroup>>
  val selectedOrder: StateFlow<OrderGroup?>
  fun loadOrders(userId: Long)
  fun loadOrderDetail(orderGroup: String)
  fun editItem(orderGroup: String, itemId: Int, newQty: Int)
  fun cancelOrder(orderGroup: String)
}

// --- DebtViewModel ---
class DebtViewModel : ViewModel() {
  val debts: StateFlow<List<Debt>>
  val activeTotal: StateFlow<Double>
  val isAllowed: StateFlow<Boolean>
  fun loadDebts(username: String)
  fun payDebt(request: DebtPayRequest)
}

// --- NotificationsViewModel ---
class NotificationsViewModel : ViewModel() {
  val notifications: StateFlow<List<Notification>>
  val unreadCount: StateFlow<Int>
  fun load(userId: Long)
  fun markRead(id: Int)
}
```

---

## 9. Navigation Graph (Jetpack Navigation)

```kotlin
NavHost(navController, startDestination = "splash") {
  composable("splash")           { SplashScreen(navController) }
  composable("login")            { LoginScreen(navController) }
  composable("home")             { HomeScreen(navController) }

  // Bottom nav destinations
  composable("menu")             { MenuScreen(navController) }
  composable("orders")           { OrdersScreen(navController) }
  composable("profile")          { ProfileScreen(navController) }

  // Nested
  composable("cart")             { CartScreen(navController) }
  composable("checkout")         { CheckoutScreen(navController) }
  composable("order_success/{orderGroup}") { OrderSuccessScreen(navController, orderGroup) }
  composable("order_detail/{orderGroup}") { OrderDetailScreen(navController, orderGroup) }
  composable("my_debt")          { MyDebtScreen(navController) }
  composable("help")             { HelpScreen(navController) }
  composable("feedback")         { FeedbackScreen(navController) }
  composable("contact_admin")    { ContactAdminScreen(navController) }
  composable("notifications")    { NotificationsScreen(navController) }
}
```

---

## 10. Supabase Client Setup (Android)

```kotlin
// build.gradle.kts (app)
dependencies {
  implementation("io.github.jan-tennert.supabase:gotrue-kt:2.6.0")
  implementation("io.github.jan-tennert.supabase:postgrest-kt:2.6.0")
}

// SupabaseClient.kt
import io.github.jan-tennert.supabase.createSupabaseClient
import io.github.jan-tennert.supabase.gotrue.SupabaseSettings

object SupabaseClient {
  val client = createSupabaseClient(
    supabaseUrl = "https://[your-project].supabase.co",
    supabaseKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  // anon key
  ) {
    install(Auth)
    install(Postgrest)
  }
}
```

If using direct Supabase reads (instead of REST API):

```kotlin
// Example: fetch menu directly
suspend fun getMenu(): List<MenuItem> {
  return SupabaseClient.client.from("menu")
    .select()
    .decodeList<MenuItem>()
}
```

---

## 11. Error Handling Strategy

| Error | Handling |
|-------|----------|
| Network timeout | Retry with exponential backoff (max 3), show "No connection" snackbar |
| 401 Unauthorized | Clear session → redirect to Login |
| 403 Forbidden | Show "This action is not allowed" |
| 404 Not Found | Show "Not found" toast |
| 429 Rate limited | Show "Too many requests. Try again in X seconds" |
| 500 Server error | Show "Something went wrong. Please try again." |
| Banned user | On ANY API call, if response indicates banned → show ban message → disable ordering |

---

## 12. AndroidManifest & Permissions

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />

<application
  android:usesCleartextTraffic="false"
  android:networkSecurityConfig="@xml/network_security_config">

  <activity android:name=".MainActivity"
    android:exported="true"
    android:windowSoftInputMode="adjustResize">
    <intent-filter>
      <action android:name="android.intent.action.MAIN" />
      <category android:name="android.intent.category.LAUNCHER" />
    </intent-filter>
  </activity>
</application>
```

---

## 13. Summary of All API Interactions

| Screen | API Calls |
|--------|-----------|
| Splash | `GET /api/auth/session` |
| Login | `POST /api/auth/request-otp`, `POST /api/auth/verify-otp` |
| Home | `GET /api/user/profile`, `GET /api/debts/active-total`, `GET /api/orders`, `GET /api/notifications` |
| Menu | `GET /api/menu` |
| Cart | (local only) |
| Checkout | `GET /api/payment-accounts`, `GET /api/debt-allow-list/check`, `POST /api/orders` |
| My Orders | `GET /api/orders` |
| Order Detail | `GET /api/orders/group/{orderGroup}` |
| My Debt | `GET /api/debts`, `GET /api/payment-accounts`, `POST /api/debts/pay` |
| Feedback | `POST /api/feedback` |
| Contact Admin | `POST /api/contact` |
| Profile | `GET /api/user/profile`, `PUT /api/user/profile` |
| Notifications | `GET /api/notifications`, `PUT /api/notifications/{id}/read` |
| Help | `GET /api/help` |
| Edit Items | `PUT /api/orders/{orderGroup}/items` |
| Cancel Order | `DELETE /api/orders/{orderGroup}` |

---

## 14. Files Required in the Android Project

```
app/
  src/main/
    java/com/shemsushop/app/
      MainActivity.kt
      ShemsuShopApp.kt                     (Application class)
      navigation/
        NavGraph.kt
      ui/
        theme/
          Color.kt, Theme.kt, Type.kt
        screens/
          splash/SplashScreen.kt
          login/LoginScreen.kt
          home/HomeScreen.kt
          menu/MenuScreen.kt
          cart/CartScreen.kt
          checkout/CheckoutScreen.kt
          orders/OrdersScreen.kt
          orderdetail/OrderDetailScreen.kt
          mydebt/MyDebtScreen.kt
          help/HelpScreen.kt
          feedback/FeedbackScreen.kt
          profile/ProfileScreen.kt
          contact/ContactAdminScreen.kt
          notifications/NotificationsScreen.kt
        components/
          OrderCard.kt
          StatusBadge.kt
          QuantityStepper.kt
          DebtCard.kt
          PaymentMethodSelector.kt
          StatusTimeline.kt
      data/
        remote/
          ApiService.kt                     (Retrofit interface)
          SupabaseClient.kt                 (optional direct access)
          dto/                              (data transfer objects)
        local/
          SessionManager.kt                 (EncryptedSharedPreferences)
        repository/
          AuthRepository.kt
          MenuRepository.kt
          OrderRepository.kt
          DebtRepository.kt
          NotificationRepository.kt
        model/
          User.kt, MenuItem.kt, OrderGroup.kt, etc.
      viewmodel/
        AuthViewModel.kt
        MenuViewModel.kt
        CartViewModel.kt
        OrdersViewModel.kt
        DebtViewModel.kt
        NotificationsViewModel.kt
      di/
        AppModule.kt                        (Hilt)
      util/
        Constants.kt
        DateUtils.kt
        NetworkResult.kt
    res/
      values/strings.xml, colors.xml
      drawable/ (icons, logo)
      xml/network_security_config.xml
    AndroidManifest.xml
  build.gradle.kts
```

---

## 15. Environment / Build Config

```kotlin
// build.gradle.kts (app module)
android {
  compileSdk = 34
  defaultConfig {
    minSdk = 26
    targetSdk = 34
    buildConfigField("String", "API_BASE_URL", "\"https://shopbotshemsu-1.onrender.com\"")
    buildConfigField("String", "SUPABASE_URL", "\"https://[your-project].supabase.co\"")
    buildConfigField("String", "SUPABASE_ANON_KEY", "\"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...\"")
  }
}
```

---

## 16. Backend API Source (Flask Extension)

The existing Flask app on Render needs these new routes. Add to `main.py`:

```python
from flask import Flask, request, jsonify
import random, uuid, asyncio
from datetime import datetime, timezone, timedelta
from database import _db

app = Flask(__name__)

@app.route("/api/auth/request-otp", methods=["POST"])
def request_otp():
    data = request.get_json()
    username = data.get("username", "").lstrip("@")
    if not username:
        return jsonify({"success": False, "error": "Username required"}), 400
    result = asyncio.run(_db(
        lambda: _supabase.table("users").select("user_id, full_name")
        .eq("username", username).limit(1).execute()
    ))
    if not result.data:
        return jsonify({"success": False, "error": "Username not found"}), 404
    user = result.data[0]
    otp = str(random.randint(100000, 999999))
    expires = datetime.now(timezone.utc) + timedelta(minutes=5)
    asyncio.run(_db(
        lambda: _supabase.table("login_otps").insert({
            "username": username, "user_id": user["user_id"],
            "otp": otp, "expires_at": expires.isoformat()
        }).execute()
    ))
    from config import BOT_TOKEN
    # Send OTP via Telegram bot
    import requests
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": user["user_id"],
            "text": f"Your Shemsu Shop login code: <b>{otp}</b>\n\nExpires in 5 minutes.",
            "parse_mode": "HTML"
        }
    )
    return jsonify({"success": True, "message": "OTP sent to your Telegram"})

@app.route("/api/auth/verify-otp", methods=["POST"])
def verify_otp():
    data = request.get_json()
    username = data.get("username", "").lstrip("@")
    otp = data.get("otp", "")
    result = asyncio.run(_db(
        lambda: _supabase.table("login_otps")
        .select("*")
        .eq("username", username)
        .eq("otp", otp)
        .eq("used", False)
        .gt("expires_at", datetime.now(timezone.utc).isoformat())
        .limit(1)
        .execute()
    ))
    if not result.data:
        return jsonify({"success": False, "error": "Invalid or expired OTP"}), 401
    record = result.data[0]
    asyncio.run(_db(
        lambda: _supabase.table("login_otps")
        .update({"used": True}).eq("id", record["id"]).execute()
    ))
    session_token = str(uuid.uuid4())
    # Store session (in-memory or DB) - for simplicity, store in user_data
    SESSIONS[session_token] = {
        "user_id": record["user_id"],
        "username": username,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    return jsonify({"success": True, "session_token": session_token})

SESSIONS = {}  # Simple in-memory store; use Redis/DB in production

@app.route("/api/auth/session", methods=["GET"])
def check_session():
    token = request.args.get("token")
    if token in SESSIONS:
        return jsonify(SESSIONS[token])
    return jsonify({"error": "Invalid session"}), 401
```
