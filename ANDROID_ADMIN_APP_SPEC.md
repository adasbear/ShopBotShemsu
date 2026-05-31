# DeliveryBot — Android Admin App Specification

## 1. Overview

A native Android app for the shop admin (`@PPopa054`, user ID `7041035485`) to manage the Telegram food ordering bot. The app connects directly to the same Supabase PostgreSQL database that the Telegram bot uses — no additional backend needed.

**Why an Android app?** The current admin interface lives inside Telegram (inline keyboards, reply keyboards). An Android app gives a native UI with real-time updates, better UX for order management, and persistent push notifications.

---

## 2. Credentials & Connection

### Supabase Project

| Field | Value |
|-------|-------|
| **Supabase URL** | `https://yqpmyowjomnbnvysbokv.supabase.co` |
| **Supabase anon/public key** | `sb_publishable_4T5Ul7YIoU_fvW5gShZo5g_abo7ixpV` |
| **Supabase service_role key** | Get from Supabase Dashboard > Settings > API > service_role key (needed for admin operations) |
| **Database** | PostgreSQL 15+ (hosted by Supabase) |

> **IMPORTANT:** Use the `service_role` key in the Android app (or a custom Supabase JWT) because `anon` key has RLS restrictions. The `service_role` key bypasses RLS. **Store it securely** — use Android Keystore or environment variables at build time. Never hardcode in source code.

### Admin Identity

| Field | Value |
|-------|-------|
| **Telegram Username** | `PPopa054` |
| **Telegram User ID** | `7041035485` |
| **Bot Token** | `8768868555:AAFriBhP04Ib9okUIbBfBiidVd55J-LVI3o` |

### Supabase SDK for Android

Use the official [Supabase Kotlin/Android SDK](https://github.com/supabase-community/supabase-kt):

```kotlin
// build.gradle.kts (app level)
implementation("io.github.jan-tennert.supabase:supabase-kt:3.1.1")
implementation("io.ktor:ktor-client-okhttp:3.1.1")
```

```kotlin
// Initialization
val supabase = createSupabaseClient(
    supabaseUrl = "https://yqpmyowjomnbnvysbokv.supabase.co",
    supabaseKey = "sb_publishable_...your_service_role_key..."
) {
    install(Postgrest)
    install(Realtime) // for live order updates
}
```

---

## 3. Database Schema (Supabase PostgreSQL)

Six tables. The app reads/writes all of them directly via Supabase REST API.

### Table: `users`

```sql
CREATE TABLE users (
    user_id    BIGINT PRIMARY KEY,
    full_name  TEXT NOT NULL,
    username   TEXT,
    banned     BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**App usage:** Display user list, ban/unban.

### Table: `menu`

```sql
CREATE TABLE menu (
    name  TEXT PRIMARY KEY,
    price NUMERIC(10,2) NOT NULL
);
```

**App usage:** CRUD menu items (add, edit price, delete).

### Table: `orders`

```sql
CREATE TABLE orders (
    id          BIGSERIAL PRIMARY KEY,
    user_id     BIGINT NOT NULL REFERENCES users(user_id),
    item        TEXT NOT NULL,
    qty         INTEGER NOT NULL CHECK (qty > 0),
    status      TEXT NOT NULL DEFAULT 'Pending',
    order_group TEXT,
    timestamp   TIMESTAMPTZ DEFAULT NOW()
);
```

**Statuses:** `Pending` → `Accepted` → `Ready` → `Delivered` | `Cancelled`

**order_group:** All items placed in a single order share the same `order_group` (format: `{user_id}_{timestamp_ms}`). Group them to show full orders.

**App usage:** View orders grouped by `order_group`, update status.

### Table: `feedback`

```sql
CREATE TABLE feedback (
    id         BIGSERIAL PRIMARY KEY,
    user_id    BIGINT NOT NULL REFERENCES users(user_id),
    name       TEXT NOT NULL,
    msg        TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**App usage:** Read feedback, optionally reply via Telegram.

### Table: `debt_allow_list`

```sql
CREATE TABLE debt_allow_list (
    id         SERIAL PRIMARY KEY,
    username   TEXT NOT NULL UNIQUE,
    added_by   BIGINT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**App usage:** View, add, remove usernames allowed to take debt.

### Table: `debts`

```sql
CREATE TABLE debts (
    id          BIGSERIAL PRIMARY KEY,
    user_id     BIGINT REFERENCES users(user_id),
    username    TEXT NOT NULL,
    amount      NUMERIC(10,2) NOT NULL,
    description TEXT,
    status      TEXT NOT NULL DEFAULT 'active',
    order_group TEXT,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    paid_at     TIMESTAMPTZ
);
```

**Statuses:** `active` → `paid` | `waived`

**App usage:** View all debts (filter by status), mark as paid, waive, auto-create from delivered orders.

---

## 4. Features & Screens

### 4.1 Splash / Login Screen

- No username/password login. The app is locked to the admin's Telegram identity.
- **Auth via Telegram Login** (preferred): Use Telegram Login Widget (https://core.telegram.org/widgets/login). The admin scans a QR or taps "Login via Telegram" → Telegram sends a payload with `id`, `first_name`, `username`, `auth_date`, `hash`. Verify the hash server-side (or locally) to confirm identity.
- **Fallback:** Simple PIN/biometric lock if Telegram auth is too complex. Hardcode check: `if (userId == 7531836547) grant access`.
- On first launch, upsert the admin into the `users` table:
  ```sql
  INSERT INTO users (user_id, full_name, username, banned)
  VALUES (7531836547, 'Admin', 'Barc_h', false)
  ON CONFLICT (user_id) DO NOTHING;
  ```

### 4.2 Dashboard (Home Screen)

Shows real-time summary cards at the top:

| Card | Data Source |
|------|------------|
| **New Orders** | COUNT of `orders` WHERE `status = 'Pending'` AND `order_group IS NOT NULL` |
| **Accepted** | COUNT of `orders` WHERE `status = 'Accepted'` |
| **Ready for Pickup** | COUNT of `orders` WHERE `status = 'Ready'` |
| **Today's Profit** | SUM of `menu.price * orders.qty` WHERE `status = 'Delivered'` AND `timestamp >= TODAY` |

Quick-action buttons below each card.

### 4.3 Orders Screen (List + Detail)

**List View:** Tab layout or segmented control:
- **Pending** (New Orders)
- **Accepted**
- **Ready**
- **All**

Each tab shows orders grouped by `order_group`. Each group displays:
- Customer name (from `users` join)
- Items list (item name × qty)
- Total cost (computed from `menu` prices)
- Timestamp (formatted)
- Action button(s)

**Detail View (tap a group):**
- Full order breakdown
- Customer info (Telegram username, user ID)
- Action buttons depending on status:
  - Pending → **Accept** / **Decline**
  - Accepted → **Mark Ready for Pickup**
  - Ready → **Mark Delivered**

**API calls:**
```kotlin
// Fetch grouped pending orders
supabase.from("orders").select(
    "id, user_id, item, qty, order_group, users(full_name)"
) { filter { eq("status", "Pending") } }

// Update status for an order group
supabase.from("orders").update({ "status" to "Accepted" }) {
    filter { eq("order_group", orderGroup) }
}
```

### 4.4 Users Screen

- List of all users from `users` table
- Each row: full name, username, banned status (badge)
- Tap → detail view
- Search bar (filter by name or username)

**User Detail:**
- Full name, username, user_id
- Order history (last 5 orders from `orders` table)
- **Ban** / **Unban** toggle button
- Ban sends a Telegram message to the user (via bot API):
  ```
  POST https://api.telegram.org/bot{TOKEN}/sendMessage
  Body: {
    "chat_id": user_id,
    "text": "You have been banned...",
    "parse_mode": "HTML"
  }
  ```

### 4.5 Menu Management Screen

- List all items from `menu` table (name + price)
- Swipe to delete (calls `DELETE FROM menu WHERE name = ?`)
- FAB (Floating Action Button) to add new item
- Tap item to edit price

**Add/Edit:** Dialog with name (if new) and price field.

### 4.6 Feedback Screen

- List of feedback entries from `feedback` table (ordered by `created_at DESC`)
- Shows: name, message preview, timestamp
- Tap → full feedback detail
- Option to send a Telegram reply to the user

### 4.7 Broadcast Screen

- Text editor (multiline EditText)
- **Send** button → fetches all user IDs from `users` table:
  ```kotlin
  supabase.from("users").select("user_id")
  ```
- Sends the same message to each via Telegram Bot API:
  ```kotlin
  // For each user_id
  httpClient.post("https://api.telegram.org/bot{TOKEN}/sendMessage") {
      setBody(mapOf("chat_id" to userId, "text" to message, "parse_mode" to "HTML"))
  }
  ```
- Show progress: count sent / total

### 4.8 Debt Management Screen

A dedicated screen to manage the debt system. Accessible from the bottom navigation or dashboard card.

**Allow List tab:**
- List of usernames approved to take debt
- Each row: `@username` (added date)
- **FAB** to add a username (text input dialog)
- Swipe to remove from allow list
- Realtime subscription to `debt_allow_list` for live updates

**Debts tab with segmented control: Active | Paid | All:**
- Each row: `@username` — Birr amount — status badge (Active 🟡 / Paid ✅ / Waived 🚫)
- Tap → **Debt Detail** view:
  - Username, amount, description
  - Status, created date, paid date (if applicable)
  - Linked order_group (tappable → navigates to order detail)
  - Action buttons:
    - **Mark Paid ✅** (if active) → sets `status = 'paid'`, `paid_at = NOW()`
    - **Waive 🚫** (if active) → sets `status = 'waived'`
- Summary card at top: total active debt amount across all users

**Delivery flow integration (inside Order Detail):**
When admin marks an order as **Delivered** (status = `Ready`), show a confirmation dialog:
- **"Mark as Paid 💰"** → status = `Delivered`, user notified "Delivered! 💰"
- **"Mark as Debt 📋"** → status = `Delivered` + insert row into `debts` table, user notified "Delivered (on debt)"

**API calls:**
```kotlin
// Fetch allow list
supabase.from("debt_allow_list").select("*").order("username")

// Add to allow list
supabase.from("debt_allow_list").insert(mapOf("username" to "user", "added_by" to adminId))

// Remove from allow list
supabase.from("debt_allow_list").delete { filter { eq("username", "user") } }

// Fetch debts (filtered)
supabase.from("debts").select("*").order("created_at", desc = true)
// With filter: .eq("status", "active")

// Mark debt as paid
supabase.from("debts").update(mapOf("status" to "paid", "paid_at" to now())) {
    filter { eq("id", debtId) }
}

// Waive debt
supabase.from("debts").update(mapOf("status" to "waived")) {
    filter { eq("id", debtId) }
}

// Get active debt total for a user
supabase.from("debts").select("amount") {
    filter { eq("username", "user"); eq("status", "active") }
}
```

### 4.9 Profit & Reports Screen

- **Today's Profit** (call `getTodaysProfit()` equivalent)
- **This Week** sum
- **This Month** sum
- Simple bar chart or list of daily totals

```sql
-- Today's profit
SELECT SUM(o.qty * m.price)
FROM orders o JOIN menu m ON o.item = m.name
WHERE o.status = 'Delivered'
  AND o.timestamp >= CURRENT_DATE;
```

---

## 5. Real-time Updates (WebSocket via Supabase Realtime)

Supabase provides Realtime (WebSocket) subscriptions. The app should subscribe to changes on the `orders` table to get instant notifications:

```kotlin
supabase.from("orders").subscribe(
    event = PostgresAction.ALL // or specific: INSERT, UPDATE
) { changes ->
    // Play sound / show notification
    // Refresh the relevant section
    when (change.newRecord["status"]) {
        "Pending" -> refreshNewOrders()
        "Accepted" -> refreshAccepted()
        "Ready" -> refreshReady()
    }
}
```

This eliminates the need for polling.

---

## 6. Push Notifications

Use **Firebase Cloud Messaging (FCM)** together with Supabase Realtime:

1. When Realtime detects a new `Pending` order → show a local notification:
   - Title: "New Order!"
   - Body: "{user_name} ordered {qty}x {item}"
2. When a banned user contacts admin (rows inserted to the admin's Telegram) → the app should also notify.

Since the bot already sends Telegram messages to the admin, the app can optionally integrate with the **Telegram Bot API to send itself messages** as a notification fallback, or simply rely on Realtime subscriptions + local notifications.

---

## 7. Telegram Bot API Integration

The app needs to send messages *to* users on behalf of the bot. Use HTTP REST calls:

```kotlin
// Send message to a user
suspend fun sendTelegramMessage(chatId: Long, text: String) {
    httpClient.post("https://api.telegram.org/bot8768868555:AAFriBhP04Ib9okUIbBfBiidVd55J-LVI3o/sendMessage") {
        setBody(json {
            put("chat_id", chatId)
            put("text", text)
            put("parse_mode", "HTML")
        })
    }
}
```

**Messages the app sends:**
| Action | Message |
|--------|---------|
| Accept order | "Your order has been accepted! Being prepared." |
| Mark ready | "Order ready for pickup! Come get it." |
| Mark delivered | "Delivered! Thank you." |
| Decline order | "Order declined. Contact admin." |
| Ban user | BAN_MESSAGE (from `utils/helpers.py`) |
| Unban user | "You have been unbanned." |
| Broadcast | User's broadcast message |

---

## 8. Android Tech Stack Recommendation

| Layer | Technology |
|-------|-----------|
| **Language** | Kotlin 100% |
| **UI** | Jetpack Compose |
| **Architecture** | MVVM (ViewModel + Repository pattern) |
| **HTTP Client** | Ktor (OkHttp engine) |
| **Supabase SDK** | [supabase-kt](https://github.com/supabase-community/supabase-kt) |
| **State Management** | StateFlow / SharedFlow |
| **DI** | Hilt or Koin |
| **Navigation** | Jetpack Navigation Compose |
| **Charts** | Vico (Compose-native charting) |
| **Auth** | Telegram Login Widget or biometric |
| **Notifications** | Firebase Cloud Messaging + Realtime |
| **Build** | Gradle with Kotlin DSL |

---

## 9. Quick-Start: SQL to Set Up Database (run in Supabase SQL Editor)

```sql
-- Ensure the admin exists in the users table
INSERT INTO users (user_id, full_name, username, banned)
VALUES (7041035485, 'Admin', 'PPopa054', false)
ON CONFLICT (user_id) DO UPDATE SET username = 'PPopa054', full_name = 'Admin';

-- Ensure order_group column exists
ALTER TABLE orders ADD COLUMN IF NOT EXISTS order_group TEXT;

-- Create debt_allow_list table
CREATE TABLE IF NOT EXISTS debt_allow_list (
    id         SERIAL PRIMARY KEY,
    username   TEXT NOT NULL UNIQUE,
    added_by   BIGINT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create debts table
CREATE TABLE IF NOT EXISTS debts (
    id          BIGSERIAL PRIMARY KEY,
    user_id     BIGINT REFERENCES users(user_id),
    username    TEXT NOT NULL,
    amount      NUMERIC(10,2) NOT NULL,
    description TEXT,
    status      TEXT NOT NULL DEFAULT 'active',
    order_group TEXT,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    paid_at     TIMESTAMPTZ
);
```

---

## 10. Folder Structure (Suggested)

```
com.shopbot.admin/
├── data/
│   ├── local/          # Room DB (offline cache, optional)
│   ├── remote/
│   │   ├── SupabaseClient.kt      # Supabase init + config
│   │   ├── TelegramBotApi.kt      # HTTP calls to Telegram API
│   │   └── dto/                   # Data Transfer Objects (matching DB tables)
│   └── repository/    # UserRepository, OrderRepository, MenuRepository, etc.
├── domain/
│   └── model/          # Domain models
├── ui/
│   ├── dashboard/      # Home/Dashboard screen
│   ├── orders/         # Orders list + detail
│   ├── users/          # Users list + detail
│   ├── menu/           # Menu management
│   ├── feedback/       # Feedback viewer
│   ├── broadcast/      # Broadcast composer
│   ├── profit/         # Profit reports
│   ├── login/          # Auth screen
│   ├── components/     # Shared Compose components
│   └── navigation/     # NavGraph
├── di/                 # Hilt/Koin modules
├── notification/       # FCM + local notifications
└── util/               # Extensions, helpers, constants
```

---

## 11. API Summary Table

| Purpose | Supabase Table | Operation |
|---------|---------------|-----------|
| Get all users | `users` | SELECT all |
| Ban user | `users` | UPDATE banned=true |
| Unban user | `users` | UPDATE banned=false |
| Get menu items | `menu` | SELECT all |
| Add menu item | `menu` | UPSERT |
| Delete menu item | `menu` | DELETE by name |
| Get grouped orders by status | `orders` + `users` join | SELECT with filter |
| Update order status | `orders` | UPDATE by order_group |
| Get today's profit | `orders` + `menu` join | SELECT aggregate |
| Get feedback | `feedback` | SELECT ordered by date |
| All user IDs | `users` | SELECT user_id only |
| Send Telegram message | — | POST to Telegram API |
| Subscribe to order changes | `orders` | Realtime subscription |
