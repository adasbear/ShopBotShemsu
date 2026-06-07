# Telegram Mini App — Technical Specification

## Overview
A single-page web app rendered inside Telegram's WebView. Users open it via a bot Menu button (`t.me/sshopdelivery_bot/app`). No authentication needed — Telegram exposes the user's identity via `Telegram.WebApp.initDataUnsafe`.

## Auth & Session
- **No OTP flow** — Telegram WebApp provides `initDataUnsafe.user` containing `id`, `username`, `first_name`.
- On launch, POST `initData` to `/api/auth/webapp-login` (new endpoint) to verify HMAC and create/get a session token.
- Alternatively, use the existing `/api/auth/session?token=...` flow by generating a lightweight token from `initData`.
- Store `user_id`, `username`, `full_name`, `token` in `localStorage`.

---

## Page Map (7 Pages)

### 1. Home / Dashboard
**Route**: `/`  
**Purpose**: Landing page after splash. Quick actions hub.

**API calls on mount**:
- `GET /api/menu` — fetch menu items for kitchen clock display
- `GET /api/debts/active-total?username={username}` — show active debt banner

**Elements**:
- Welcome message: "Hi {first_name} 👋"
- Active debt banner (if > 0) with "Pay Now" button → `/debt`
- Quick action grid (2×2):
  - **Order Now** → `/menu`
  - **My Orders** → `/orders`
  - **My Debt** → `/debt`
  - **Help** → `/help`
- Bottom navigation bar: Home | Menu | Orders | Profile

---

### 2. Menu
**Route**: `/menu`  
**Purpose**: Browse categories, select items, add to cart.

**API calls**:
- `GET /api/menu` — fetch all items (categories have `price=0.0`, sub-items have `parent`)

**State**:
- `categories`: filter from menu where `price == 0.0`
- `selectedCategory`: currently active category (null = show all sub-items)
- `cart`: Map<itemName, {qty, price, comment}> held in global state

**Flow**:
1. On load, fetch menu from API
2. Show category chips horizontally (scrollable)
3. Below: 2-column grid of sub-items for the selected category
4. Each item card: name, price (Birr), "+" button
5. "+" button increments qty in cart (or adds new entry)
6. Floating bar at bottom when cart is non-empty: "X items — Birr Y.ZZ" | "View Cart" button
7. "View Cart" → `/cart`

**Bot features mapped**:
- ✅ Click category → see sub-items (equals bot's category drill-down)
- ✅ Add to cart (equals bot's "select item → enter qty")
- ✅ "Other ✏️" NOT included (removed from bot as well)

---

### 3. Cart & Checkout
**Route**: `/cart`  
**Purpose**: Review cart, set quantities, add comment, choose payment, place order.

**State**:
- `cart`: list of `{name, price, qty, comment}`
- `paymentMethod`: "CBE Transfer" | "Telebirr" | "Debt"
- `selectedAccountId`: int (for CBE/Telebirr)
- `transactionRef`: string (SMS confirmation)
- `specialInstructions`: string

**API calls**:
- `GET /api/payment-accounts` — on mount, fetch bank accounts
- `GET /api/debt-allow-list/check?username={username}` — check debt eligibility
- `POST /api/orders` — place order
- `POST /api/orders` body:
```json
{
  "user_id": int,
  "username": "string",
  "full_name": "string",
  "items": [{"item": "name", "qty": int, "price": float}],
  "payment_method": "CBE Transfer|Telebirr|Debt",
  "payment_account_id": int|null,
  "confirmation": "string|null",
  "comment": "string|null"
}
```
Returns: `{"success": true, "order_group": "APP-...", "total": float}`

**Flow**:
1. Show cart items list with `-` / `qty` / `+` controls and delete button
2. Subtotal + Birr 80 delivery fee
3. "Proceed to Checkout" button
4. Checkout page:
   - Payment method selection (3 radio tiles)
   - If CBE/Telebirr: show account list, select one, enter transaction ref textarea
   - If Debt: show allowance status
   - Special instructions textarea
   - Order summary (items, subtotal, delivery fee, total)
   - "Place Order" button
5. On success → `/order-success?ref=APP-...`

**Bot features mapped**:
- ✅ Choose payment method (CBE/Telebirr/Debt)
- ✅ Select bank account
- ✅ Paste SMS confirmation
- ✅ Special instructions
- ✅ View total with delivery fee

---

### 4. Order Success
**Route**: `/order-success?ref={orderGroup}`  
**Purpose**: Confirmation after placing order.

**Elements**:
- Checkmark icon
- "Order Placed!"
- Reference: `APP-xxMMdd-xxxx`
- "We'll notify you when it's accepted."
- "Track My Orders" button → `/orders`
- "Back to Home" button → `/`

---

### 5. My Orders
**Route**: `/orders`  
**Purpose**: View all orders, tap to see details, cancel if Pending.

**API calls on mount**:
- `GET /api/orders?user_id={userId}` — returns raw order items array

**Client-side grouping**:
- Group raw items by `order_group`
- For each group, collect: status (from any item), items list, timestamps
- Sort by most recent

**Tabs**: Active | History
- Active: status = Pending or Accepted
- History: all others (Ready, Arrived, Delivered, Cancelled)

**Each order card**:
- Order group ref (`APP-...`)
- Status pill (colored: Pending=yellow, Accepted=green, Cancelled=red)
- Item summary: "2x Pizza, 1x Pasta"
- Total: "Birr X.XX"
- Timestamp
- Tap → `/order-detail?group={orderGroup}`

**Bot features mapped**:
- ✅ View all orders grouped
- ✅ Active vs History filtering
- ✅ Status indicators

---

### 6. Order Detail
**Route**: `/order-detail?group={orderGroup}`  
**Purpose**: Full order breakdown, status timeline, cancel action.

**API calls on mount**:
- `GET /api/orders/group/{orderGroup}` — returns:
```json
{
  "order_group": "APP-...",
  "items": [{"id": 1, "item": "Pizza", "qty": 2, "status": "Pending", "timestamp": "..."}],
  "total": 450.0,
  "payment": "CBE Transfer:1:REF123",
  "comment": "No onions please",
  "decline_reason": null,
  "status": "Pending",
  "created_at": "..."
}
```

**API calls on action**:
- `DELETE /api/orders/{orderGroup}` — cancel the order

**Elements**:
- **Status timeline** (4 steps):
  - Placed ●━━━━ Preparing ●━━━━ Ready ●━━━━ Delivered
  - Active steps are orange, inactive steps are grey
- **Items list**: item name, qty, price each
- **Payment info**: which method/account/ref used
- **Special instructions**: if any
- **Decline reason** (only if status = Cancelled): red warning box
- **Cancel button** (only if status = Pending): confirmation dialog → DELETE API call

**Bot features mapped**:
- ✅ Edit items — NOT available in mini app (bot-only feature since it's complex; user can cancel and re-order)
- ✅ Cancel order (only if Pending) — mapped
- ✅ Order timeline — mapped
- ✅ View decline reason — mapped
- ✅ View payment info — mapped
- ✅ View special instructions — mapped

---

### 7. My Debt
**Route**: `/debt`  
**Purpose**: View outstanding balance, pay debt.

**API calls on mount**:
- `GET /api/debts?username={username}` — all debt records
- `GET /api/debts/active-total?username={username}` — active total
- `GET /api/payment-accounts` — bank accounts for payment

**API calls on action**:
- `POST /api/debts/pay` — submit debt payment

**Body**:
```json
{
  "username": "string",
  "user_id": int,
  "amount": float,
  "payment_account_id": int,
  "confirmation": "string"
}
```

**Flow**:
1. Show outstanding balance banner (Birr X.XX)
2. If balance > 0: "Settle Debt" form
   - Amount input
   - Select payment account from list
   - Transaction reference input
   - "Pay Now" button
3. Payment history list (all debts, paid + active)
4. Each entry: amount, description, status pill

**Bot features mapped**:
- ✅ View debt balance
- ✅ Pay debt (select account → enter ref → submit)
- ✅ Payment history

---

### 8. Profile
**Route**: `/profile`  
**Purpose**: User info, settings, account services.

**Elements**:
- Avatar circle (first letter of name)
- Full name (editable inline — tap pencil → edit → save)
- Username `@username`
- "Gold Patron" badge
- Service list:
  - **Notifications** → `/notifications` (with unread badge count)
  - **Contact Admin** → `/contact-admin`
  - **Help** → `/help`
  - **Feedback** → `/feedback`
- **Logout** button → clear localStorage → close mini app

**Bot features mapped**:
- ✅ View/edit name
- ✅ Access to notifications, contact, help, feedback
- ✅ Logout

---

### 9. Notifications
**Route**: `/notifications`  
**Purpose**: Read system notifications.

**API calls on mount**:
- `GET /api/notifications?user_id={userId}` — returns array of `{id, title, body, order_group, read, created_at}`

**API calls on action**:
- `PUT /api/notifications/{id}/read` — mark as read

**Flow**:
1. Fetch notifications on mount
2. Show list: each item has icon, title, body, timestamp
3. Unread items have orange dot on left
4. Tap item → mark as read (PUT) + optionally navigate to related order
5. Empty state: "No notifications"

**Bot features mapped**:
- ✅ View notifications
- ✅ Read/unread indicators

---

### 10. Contact Admin
**Route**: `/contact-admin`  
**Purpose**: Send a message to the admin.

**API calls**:
- `POST /api/contact` — send message

**Body**:
```json
{
  "user_id": int,
  "username": "string",
  "message": "string"
}
```

**Flow**:
1. Simple form: message textarea + "Send" button
2. After send: "Message sent! Admin will respond via notification."
3. No chat UI — just a one-way message form (admin responds via bot)

**Bot features mapped**:
- ✅ Contact admin
- Note: bot has interactive chat, mini app uses simple form + notification response

---

### 11. Feedback
**Route**: `/feedback`  
**Purpose**: Submit feedback/rating.

**API calls**:
- `POST /api/feedback` — submit

**Body**:
```json
{
  "user_id": int,
  "msg": "string (rating + comment combined)"
}
```
Note: API only has `msg` field (no separate rating). Send `"Rating: 4/5 - Great food!"` as the msg.

**Flow**:
1. 5-star rating component (visual only, stored as text in msg)
2. Comment textarea
3. Submit button
4. After submit: success screen "Thank you!"

**Bot features mapped**:
- ✅ Submit feedback

---

### 12. Help
**Route**: `/help`  
**Purpose**: Frequently Asked Questions.

**Elements**:
- Expandable FAQ cards (4 categories):
  - **Orders**: placing, cancelling, editing
  - **Payments**: methods, debt, bank transfer
  - **Debt**: eligibility, payment
  - **Delivery**: timing, address
- Each card: category title (tap to expand/collapse), Q&A pairs inside

**No API calls** — static content.

**Bot features mapped**:
- ✅ Help system with expandable categories

---

## API Reference Summary

| Method | Endpoint | Params/Body | Returns |
|--------|----------|-------------|---------|
| GET | `/api/menu` | `?parent=name` (optional) | `[{id, name, price, parent, available}]` |
| GET | `/api/payment-accounts` | — | `[{id, bank_name, number, holder_name}]` |
| GET | `/api/debt-allow-list/check` | `?username=` | `{allowed: bool}` |
| GET | `/api/debts` | `?username=` | `[{id, username, amount, description, status, created_at, paid_at}]` |
| GET | `/api/debts/active-total` | `?username=` | `{active_total: float}` |
| POST | `/api/debts/pay` | `{username, user_id, amount, payment_account_id, confirmation}` | `{success: bool}` |
| GET | `/api/orders` | `?user_id=` | `[{id, item, qty, status, order_group, timestamp}]` |
| GET | `/api/orders/group/{group}` | — | `{order_group, items, total, payment, comment, decline_reason, status, created_at}` |
| POST | `/api/orders` | `{user_id, username, full_name, items, payment_method, payment_account_id, confirmation, comment}` | `{success, order_group, total}` |
| DELETE | `/api/orders/{group}` | — | `{success: bool}` |
| GET | `/api/notifications` | `?user_id=` | `[{id, title, body, order_group, read, created_at}]` |
| PUT | `/api/notifications/{id}/read` | — | `{success: bool}` |
| POST | `/api/feedback` | `{user_id, msg}` | `{success: bool}` |
| POST | `/api/contact` | `{user_id, username, message}` | `{success: bool}` |

## Bot Features NOT in Mini App (intentional)
- **Edit items in existing order** — bot-only; user can cancel and re-order instead
- **Admin features** (manage menu, users, orders, debt) — admin-only by design
- **"No Item" / Decline flows** — admin-initiated
- **Lock Menu / Daily Stock** — admin-initiated; if stock = 0, menu item simply appears sold out
- **Registration flow** — not needed (Telegram provides identity via WebApp)

## New Endpoint Required
- `POST /api/auth/webapp-login` — accepts `{initData: string}`, verifies HMAC with bot token, creates/returns session token with user_id, username, full_name. This replaces the OTP flow for the mini app.

## Architecture
- **Framework**: Vanilla HTML/CSS/JS (or lightweight framework like Preact/Svelte for SPA)
- **Hosting**: Render static site or GitHub Pages
- **State**: Simple global JS object + localStorage for session
- **Navigation**: Hash-based routing (`#/menu`, `#/orders`, etc.)
- **HTTP**: `fetch()` with `Authorization: Bearer {token}` header
- **WebApp integration**: `Telegram.WebApp.ready()`, `Telegram.WebApp.expand()`, `Telegram.WebApp.close()` on logout
- **Backend**: Existing Flask API at `https://shopbotshemsu-1.onrender.com/`
