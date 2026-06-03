# Shemsu Shop — Mobile App Developer Prompt

## Overview

Shemsu Shop is a food ordering system. Customers order via a Telegram bot (`@ShemsuShopBot`). We are now building an **Android companion app** that lets customers browse the menu, place orders, manage debt, and track orders — all reading/writing the **same Supabase database** as the bot. The admin still manages everything through the Telegram bot (no admin screens in the app).

**Critical rule:** The bot is the entry point. Users **must** first start the bot (`@ShemsuShopBot`), register their name, and have a row in the `users` table before they can log into the app. This ensures the bot has the user's Telegram chat_id to deliver OTPs and order notifications.

---

## Credentials

```
Supabase URL:    https://[your-project].supabase.co
Supabase anon key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... (get from Supabase Settings → API → anon public)
Bot username:    @ShemsuShopBot
API base URL:    https://shopbotshemsu-1.onrender.com
```

---

## Complete SQL Schema

Run this once in Supabase SQL Editor. All tables already exist except `login_otps` and `sessions` (add these).

```sql
-- 1. users — registered by the bot when user sends /start
CREATE TABLE IF NOT EXISTS users (
  user_id BIGINT PRIMARY KEY,
  full_name TEXT NOT NULL,
  username TEXT,
  banned BOOLEAN DEFAULT FALSE,
  phone TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. menu — categories (price=0) and sub-items (price>0)
CREATE TABLE IF NOT EXISTS menu (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  price NUMERIC NOT NULL DEFAULT 0,
  parent TEXT REFERENCES menu(name) ON DELETE CASCADE,
  available BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. orders — one row per item per order group
CREATE TABLE IF NOT EXISTS orders (
  id SERIAL PRIMARY KEY,
  user_id BIGINT REFERENCES users(user_id),
  item TEXT NOT NULL,
  qty INTEGER NOT NULL,
  status TEXT DEFAULT 'Pending',
  order_group TEXT,
  timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- 4. order_comments — special instructions per order group
CREATE TABLE IF NOT EXISTS order_comments (
  id SERIAL PRIMARY KEY,
  order_group TEXT UNIQUE NOT NULL,
  comment TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. order_payments — bank confirmation per order group
CREATE TABLE IF NOT EXISTS order_payments (
  order_group TEXT PRIMARY KEY,
  payment_info TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. order_decline_reasons — admin's cancellation reason
CREATE TABLE IF NOT EXISTS order_decline_reasons (
  order_group TEXT PRIMARY KEY,
  reason TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. feedback — user ratings
CREATE TABLE IF NOT EXISTS feedback (
  id SERIAL PRIMARY KEY,
  user_id BIGINT,
  name TEXT,
  msg TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 8. debt_allow_list — who may take debt
CREATE TABLE IF NOT EXISTS debt_allow_list (
  id SERIAL PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  added_by BIGINT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 9. debts — individual debt records
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

-- 10. debt_payments — payments made toward debt
CREATE TABLE IF NOT EXISTS debt_payments (
  id SERIAL PRIMARY KEY,
  username TEXT NOT NULL,
  user_id BIGINT,
  amount NUMERIC NOT NULL,
  payment_info TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 11. payment_accounts — admin-managed bank accounts
CREATE TABLE IF NOT EXISTS payment_accounts (
  id SERIAL PRIMARY KEY,
  bank_name TEXT NOT NULL,
  number TEXT NOT NULL,
  holder_name TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 12. login_otps — OTP codes for app login
CREATE TABLE IF NOT EXISTS login_otps (
  id SERIAL PRIMARY KEY,
  username TEXT NOT NULL,
  user_id BIGINT,
  otp TEXT NOT NULL,
  expires_at TIMESTAMPTZ NOT NULL,
  used BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 13. sessions — app session tokens
CREATE TABLE IF NOT EXISTS sessions (
  token UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id BIGINT NOT NULL REFERENCES users(user_id),
  username TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '30 days')
);

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

-- Indexes
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_order_group ON orders(order_group);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_debts_username ON debts(username);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_menu_parent ON menu(parent);
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);

-- Default payment accounts
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

## Authentication Flow

### Step 1: Check registration (app-side)
When user opens app, first tell them: *"Open Telegram, start @ShemsuShopBot, and type /start to register."*

The app can optionally call `POST /api/auth/check-user` with a username to see if they're registered before allowing login.

### Step 2: Request OTP

**`POST /api/auth/request-otp`**

```json
// Request
{ "username": "PPopa054" }

// Success (user exists in database)
{ "success": true, "delivery": "bot" }

// Success (user not found — no registration)
{ "error": "User not registered. First start @ShemsuShopBot on Telegram." }
```

The bot sends an OTP to the user's Telegram DM. User checks Telegram, sees:

```
Shemsu Shop Login Code

483921

Expires in 5 minutes.
```

### Step 3: Verify OTP

**`POST /api/auth/verify-otp`**

```json
// Request
{ "username": "PPopa054", "otp": "483921" }

// Success
{ "success": true, "session_token": "a1b2c3d4-e5f6-7890-abcd-ef1234567890", "is_new_user": false }
```

### Step 4: Check session (app launch / resume)

**`GET /api/auth/session?token=a1b2c3d4-e5f6-7890-abcd-ef1234567890`**

```json
// Valid
{ "user_id": 7041035485, "username": "PPopa054", "full_name": "Adil" }

// Invalid / expired
{ "error": "Invalid or expired session" }
```

Store `session_token` in `EncryptedSharedPreferences`. On app launch, call this endpoint. If valid → go to Home. If invalid → go to Login.

---

## Why Username-Based Auth Is Secure

- User must **control the Telegram account** to receive the OTP
- User must know their **exact Telegram username** (case-sensitive, without @)
- OTP is **6 digits, 5-minute expiry, single-use**
- Rate-limited: **max 3 OTPs per username per hour**
- Brute force impossible: each wrong attempt consumes the OTP (single-use)

---

## All API Endpoints

All endpoints return JSON. Include `Content-Type: application/json`.

### Auth

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/auth/request-otp` | Send OTP to user's Telegram DM |
| POST | `/api/auth/verify-otp` | Verify OTP, get session token |
| GET | `/api/auth/session?token=X` | Validate session, get user info |

### User Profile

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/user/profile?user_id=X` | Get user data |
| PUT | `/api/user/profile` | Update full name |

### Menu

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/menu` | All items (categories + sub-items) |
| GET | `/api/menu?parent=Breakfast` | Filter by category |

### Payment Accounts (checkout display)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/payment-accounts` | Available bank accounts to pay into |

### Debt Allow Check

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/debt-allow-list/check?username=X` | Is user allowed to take debt? |

### Orders

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/orders` | Place a new order |
| GET | `/api/orders?user_id=X` | Get all user orders (group in app) |
| GET | `/api/orders/group/{order_group}` | Full order detail + payment + comment |
| PUT | `/api/orders/{order_group}/items` | Edit item quantities |
| DELETE | `/api/orders/{order_group}` | Cancel order |

### Debts

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/debts?username=X` | All debt records + active total |
| POST | `/api/debts/pay` | Record a debt payment |

### Notifications

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/notifications?user_id=X` | Notification history |
| PUT | `/api/notifications/{id}/read` | Mark notification as read |

### Other

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/feedback` | Submit feedback |
| POST | `/api/contact` | Send message to admin |

---

## Detailed Endpoint Specs

### POST /api/orders — Place an order

```json
{
  "user_id": 7041035485,
  "username": "PPopa054",
  "full_name": "Adil",
  "items": [
    { "item": "Fetira", "qty": 4, "price": 160.0 }
  ],
  "payment_method": "pay",
  "payment_account_id": 4,
  "confirmation": "Transfer of 640.00 ETB to Telebirr 0907319664 successful. Ref: TRF-12345",
  "comment": "No sugar please"
}
```

**Response:**
```json
{
  "success": true,
  "order_group": "7041035485_1717200000123",
  "total": 640.0,
  "payment_method": "pay",
  "status": "Pending"
}
```

For **debt** orders: set `"payment_method": "debt"`, omit `payment_account_id` and `confirmation`.

### PUT /api/orders/{order_group}/items — Edit quantities

```json
{
  "items": [
    { "id": 1, "qty": 5 }
  ]
}
```

### GET /api/orders/group/{order_group} — Full detail

**Response:**
```json
{
  "order_group": "7041035485_1717200000123",
  "items": [
    { "id": 1, "item": "Fetira", "qty": 4, "status": "Pending" }
  ],
  "total": 640.0,
  "payment": "Telebirr - 0907319664 (Alazar)\nConfirmation: Transfer of 640.00 ETB...",
  "comment": "No sugar please",
  "decline_reason": null,
  "status": "Pending",
  "created_at": "2025-06-01T12:00:00Z"
}
```

### GET /api/debts?username=PPopa054

**Response:**
```json
{
  "active_total": 500.0,
  "records": [
    { "id": 1, "username": "PPopa054", "amount": 500.0, "description": "Order #...", "status": "active", "created_at": "..."}
  ]
}
```

### POST /api/debts/pay — Pay debt

```json
{
  "username": "PPopa054",
  "user_id": 7041035485,
  "amount": 500.0,
  "payment_account_id": 4,
  "confirmation": "Transfer of 500.00 ETB to Telebirr 0907319664 successful."
}
```

---

## App Screens & Navigation

```
Splash Screen
  ├── No session → Login Screen
  │                   └── Enter Telegram username
  │                   └── Wait for OTP
  │                   └── Enter OTP → verified → Home
  └── Has session → Home Screen
                      │
    ┌─────────────────┼──────────────────┐
    Home              Menu               Orders             Profile
    │                 │                  │                  │
    ├─ Quick actions  ├─ Categories      ├─ Active tab      ├─ Edit name
    ├─ Active debt    ├─ Sub-items       ├─ History tab     ├─ Feedback
    ├─ Recent orders  ├─ Cart → Checkout └─ Order detail    ├─ Contact admin
    └─ Help           └─ Search            ├─ Edit items    └─ Logout
                                          └─ Cancel order
```

### Screen Details

**1. Splash** (2s): logo, loading spinner, check session token → route

**2. Login**: 
- Instruction text: "Open Telegram, start @ShemsuShopBot, and type /start first."
- Input: Telegram username
- Button: "Send OTP"
- After OTP sent: 6-digit input fields
- Timer: 5-minute countdown
- Error states: "Not registered. Start the bot first.", "Invalid OTP", "Too many requests"

**3. Home**:
- Greeting: "Hi, {{full_name}} 👋"
- Active debt card (if > 0): "Active Debt: Birr X.XX — Tap to pay"
- Quick actions (2×2 grid): Order Now, My Orders, My Debt, Help
- Recent orders (last 3, horizontal scroll)
- Bottom nav: Home | Menu | Orders | Profile

**4. Menu**:
- Search bar at top
- Category chips (horizontal scroll): "All", "Breakfast", "Drinks", etc.
- Items grid (2 columns): name, price, quantity stepper
- Category chips filter the grid
- "Other ✏️" card at bottom → custom item name + quantity
- Cart FAB with badge count → Cart screen

**5. Cart**:
- Items list with quantity stepper per row, swipe to delete
- Special instructions field (expandable)
- Subtotal: "Birr X.XX"
- "Continue to Pay" button
- "Add More Items" text button

**6. Checkout / Payment**:
- Order summary (read-only)
- Payment method selection (radio list from `/api/payment-accounts`)
- "Take on Debt" card (conditional, check `/api/debt-allow-list/check`)
- If paying: show bank details, confirmation field, ⚠️ No screenshots warning
- If debt: confirm dialog
- Submit → success screen

**7. My Orders**:
- Two tabs: Active (Pending/Accepted/Ready) | History (Delivered/Cancelled)
- Order cards: date, status badge, item count, total, paid/debt icon
- Tap → Order Detail

**8. Order Detail**:
- Status timeline: Ordered → Accepted → Ready → Delivered (or Cancelled with reason)
- Items list
- Payment info
- Comment
- Edit/Cancel buttons (only if Pending AND before 6PM UTC)

**9. My Debt**:
- Active total header
- Debt records list with status
- "Pay Now" button (if active > 0) → payment flow

**10. Profile**:
- Name (editable), username (read-only)
- Settings: notification toggle
- Feedback button
- Contact Admin button
- Logout

**11. Help**: Expandable FAQ categories

**12. Notifications**: List from `/api/notifications`, tap → order detail

---

## Important Business Rules

### 6PM Edit/Cancel Rule
Orders can only be edited or cancelled if:
1. Status is **Pending**
2. The order was placed **today** AND current UTC time is **before 18:00 (6PM UTC)**

The API enforces this on `PUT /api/orders/{group}/items` and `DELETE /api/orders/{group}`. If blocked, return 403 with error.

Local time in Ethiopia is UTC+3, so 6PM UTC = 9PM local time.

### Menu Categories vs Sub-items
- Items with `price = 0.0` are **categories** (not orderable directly)
- Items with `price > 0` are **orderable sub-items**
- The app should display categories as headers/chips, and show sub-items under them
- Categories have `parent = null`, sub-items have `parent = "CategoryName"`

### Debt
- Only users in `debt_allow_list` can place orders on debt
- Check `/api/debt-allow-list/check?username=X` before showing the debt option
- If not allowed, hide the debt option entirely

### Currency
All prices are in **Ethiopian Birr**. Display as `"Birr X.XX"` or `"Birr X"`.

---

## Data Models (Kotlin)

```kotlin
data class User(
  val user_id: Long,
  val full_name: String,
  val username: String?,
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
  val total: Double
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
```

---

## Error Handling

Every API endpoint returns:
- `2xx` — success
- `4xx` — client error (invalid input, auth failure, rate limit)
- `5xx` — server error

**Response format for errors:**
```json
{ "error": "Description of what went wrong" }
```

Handle these in the app:
| HTTP Status | Meaning | App Action |
|-------------|---------|-----------|
| 400 | Bad request | Show field validation error |
| 401 | Unauthorized | Clear session → redirect to Login |
| 403 | Forbidden | Show "Action not allowed" (banned / 6PM rule) |
| 404 | Not found | Show "Not found" toast |
| 429 | Rate limited | Show "Too many requests. Wait X minutes." |
| 500 | Server error | Show "Something went wrong. Try again." |

---

## Supabase Direct Read (Optional)

For faster read-only data (menu, payment accounts), the app can read directly from Supabase using the anon key:

```kotlin
// build.gradle.kts
implementation("io.github.jan-tennert.supabase:postgrest-kt:2.6.0")

// SupabaseClient.kt
val client = createSupabaseClient(
    supabaseUrl = "https://[your-project].supabase.co",
    supabaseKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  // anon key
) {
    install(Postgrest)
}

// Fetch menu
suspend fun getMenu(): List<MenuItem> {
    return client.from("menu")
        .select()
        .decodeList<MenuItem>()
}
```

All writes (orders, debt payments, feedback) must go through the API to trigger admin notifications.

---

## Project Structure

```
app/src/main/java/com/shemsushop/app/
  MainActivity.kt
  ShemsuShopApp.kt
  navigation/NavGraph.kt
  ui/
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
      profile/ProfileScreen.kt
      notifications/NotificationsScreen.kt
    components/
      OrderCard.kt, StatusBadge.kt, QuantityStepper.kt, etc.
  data/
    remote/ApiService.kt (Retrofit)
    model/ (data classes)
    repository/
  viewmodel/
  di/
  util/
```

Backend API base URL: `https://shopbotshemsu-1.onrender.com`
