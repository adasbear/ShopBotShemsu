# Shemsu Shop — Android App Specification

## Overview

A native Android companion app for the Shemsu Shop Telegram bot. Users browse the menu, place orders, manage debt, track order status, and communicate with the admin — all without opening Telegram. Admin notifications are still sent via the Telegram bot (no changes to the admin side).

---

## Authentication

### How login works
1. User opens the app for the first time → sees **Login Screen**
2. Enters their **Telegram username** (e.g., `@PPopa054`)
3. App calls backend → the Telegram bot sends a **6-digit OTP** directly to that user's Telegram DM
4. User enters the OTP in the app → verified → app stores `user_id`, `username`, `full_name` from Supabase locally
5. Session persists (shared prefs / DataStore) — no re-login unless user logs out

### Backend requirement
- A lightweight REST API endpoint `POST /api/auth/request-otp` and `POST /api/auth/verify-otp`
- The API calls the bot's `context.bot.send_message()` to deliver the OTP
- OTPs stored in a new Supabase table `login_otps` with 5-minute expiry

---

## Screens

### 1. Splash Screen
- App logo (Shemsu Shop branding)
- Loading indicator
- Check for saved session → route to **Home** or **Login**
- Duration: ~2s

### 2. Login Screen
- App logo at top
- Text field: "Enter your Telegram username"
- "Send OTP" button → calls `POST /api/auth/request-otp`
- OTP input field (6 digits) appears after OTP is sent
- "Verify" button → calls `POST /api/auth/verify-otp`
- On success → save session → navigate to **Home**
- Error states: "Username not found", "Invalid OTP", "OTP expired"

### 3. Home Screen (Dashboard)
- **Top section**: User greeting ("Hi, {{full_name}} 👋")
- **Active debt card** (if debt > 0): "Active Debt: Birr X.XX — Pay Now →"
- **Quick action grid** (2×2):
  - 🛒 **Order Now** → Menu screen
  - 📦 **My Orders** → My Orders screen
  - 💰 **My Debt** → My Debt screen  
  - ❓ **Help** → Help screen
- **Recent orders** (last 3, scrolling): order_group, status badge, total
- **Bottom navigation bar**: Home | Menu | Orders | Profile

### 4. Menu Screen
- **Top bar**: Search icon + cart icon (with badge count)
- **Category chips** (horizontal scrollable): e.g., "All", "Breakfast", "Lunch", "Drinks"
- **Item grid** (2 columns) or list view toggle:
  - Each item card: image placeholder, name, price ("Birr X.XX")
  - Categories show a ▶️ indicator → tapping drills into sub-items
  - Sub-items (price > 0) show "Add +" button
- **Bottom section**: "Other ✏️" card → custom item request (name + quantity)
- **Search**: Full-text search across item names
- **Cart floating button**: shows total items count → opens Cart screen

### 5. Item Detail / Add to Cart
- When user taps a sub-item (or "Other"): full-screen bottom sheet
- Item name, price
- Quantity stepper (— 1 +)
- "Add to Cart" button
- For "Other ✏️": text field for item name + quantity stepper

### 6. Cart Screen
- List of added items:
  - Item name, quantity, line total
  - Swipe to delete or edit quantity
- **Special instructions** field (optional) — collapsed by default, expand to type
- **Summary section**: Subtotal (Birr X.XX)
- **Buttons**:
  - "Continue to Pay" (primary)
  - "Add More Items" → back to Menu

### 7. Checkout / Payment Screen
- **Order summary** (read-only): item list, total
- **Payment method selection** (radio list):
  - CBE — 1000404793199
  - Abyssinia — 1000092847899
  - Awash — 1000092847898  
  - Telebirr — 0907319664
  - All under name "Alazar"
- **Option card**: "Take on Debt 📋" (below payment methods, only if user is on allow list)
- **Confirmation step** (after selecting a payment method):
  - Bank name, account number, holder name displayed
  - Text field: "Paste your bank/Telebirr confirmation message"
  - ⚠️ Warning: "Do not send screenshots — paste text only"
  - "Submit Payment" button
- **Debt flow**: If user selects debt → confirm dialog → "Order placed on debt!"
- **Success screen**: "Order submitted successfully and payment info is awaiting approval."

### 8. My Orders Screen
- **Tab layout**: Active | History
  - **Active tab**: Pending, Accepted, Ready orders (ordered by newest first)
  - **History tab**: Completed, Cancelled orders
- Each order card shows:
  - Order group ID (truncated), date
  - Status badge (colored: 🟡 Pending, 🟢 Accepted, 🟠 Ready, ✅ Delivered, ❌ Cancelled)
  - Item count, total price
  - Payment status (Paid / Debt) with icon
- Tap a card → **Order Detail screen**

### 9. Order Detail Screen
- **Status timeline** (vertical stepper):
  - 🟢 Ordered — timestamp
  - 🟡 Accepted — timestamp
  - 🟠 Ready — timestamp
  - ✅ Delivered — timestamp (or ❌ Cancelled with reason)
- **Items section**: item name × qty = line total
- **Total**: Birr X.XX
- **Payment section**: method, confirmation text (if paid)
- **Comment section**: special instructions (if any)
- **Action buttons** (only if status is Pending AND before 6PM UTC):
  - "Edit Items" → opens quantity editor
  - "Cancel Order" → confirm dialog → cancels order

### 10. My Debt Screen
- **Header card**: "Active Debt: Birr X.XX"
- **Debt list**: each record shows:
  - Description (e.g., "Order #...")
  - Amount
  - Status icon + label (Active 🕐, Paid ✅, Waived 🚫)
- **"Pay Now 💰" button** (if active debt > 0) → same payment flow as Checkout
  - Select payment method → paste confirmation → submitted
  - On success: "Debt payment of Birr X.XX submitted!"
- Empty state: "No debt records. Great job! 🎉"

### 11. Help Screen
- **Category list** (vertical, expandable cards):
  - "How to Order"
  - "Bot Not Responding"
  - "Custom Requests"
  - "Edit / Cancel Orders"
  - "Contact Admin"
- Each card expands to show full text content
- **Bottom button**: "Contact Admin" → opens Contact Admin screen

### 12. Feedback Screen
- **Rating** (1–5 stars)
- **Message field** (multiline)
- "Submit" button
- Success: "Thanks for your feedback! 🙏"

### 13. Profile Screen
- **User info card**:
  - Full name (editable)
  - Telegram username (read-only)
  - Phone number (read-only)
- **Settings section**:
  - Notifications toggle (on/off)
- **Danger zone**:
  - "Log Out" button → clears session → back to Login

### 14. Contact Admin Screen
- **Chat-like interface** (simple message list):
  - User messages shown right-aligned
  - Admin replies shown left-aligned (pulled from bot messages via Supabase)
- **Input field** at bottom + Send button
- **Fallback**: For banned users, the screen shows a notice: "You are banned. Contact admin via @PPopa054 on Telegram."

### 15. Notifications Screen
- Accessed from system notification tap or from Profile
- List of past notifications:
  - "Order Accepted ✅"
  - "Order Ready for Pickup 🟠"
  - "Order Declined ❌ — Reason: ..."
  - "Debt Payment Received"
- Tap → navigates to relevant Order Detail screen

---

## Navigation Structure

```
Splash
  └→ Login (if no session)
  └→ Home (if session exists)
       ├── Bottom Nav: Home | Menu | Orders | Profile
       │
       ├── Home
       │    ├── Order Now → Menu
       │    ├── My Orders → Orders
       │    ├── My Debt → My Debt
       │    └── Help → Help
       │
       ├── Menu
       │    ├── Category → Sub-items grid
       │    │    └── Item → Add to Cart bottom sheet
       │    │         └── Cart
       │    │              └── Checkout
       │    │                   ├── Payment (method → confirmation → success)
       │    │                   └── Debt → success
       │    └── Other ✏️ → custom item input → Cart
       │
       ├── Orders
       │    ├── Active tab → Order Detail
       │    │    ├── Edit Items
       │    │    └── Cancel Order
       │    └── History tab → Order Detail
       │
       └── Profile
            ├── Edit Name
            ├── Settings
            ├── Feedback → Feedback screen
            └── Log Out
```

---

## Backend / API Endpoints

The app communicates with a lightweight REST API (can be a separate Flask/FastAPI service or extension of the existing one).

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/auth/request-otp` | Send OTP to user's Telegram |
| POST | `/api/auth/verify-otp` | Verify OTP, return session token |
| GET | `/api/user/profile` | Get user data (user_id, name, username) |
| PUT | `/api/user/profile` | Update full name |
| GET | `/api/menu` | Get all menu items (flat or nested) |
| POST | `/api/orders` | Place a new order |
| GET | `/api/orders?user_id=X` | Get user's orders (grouped) |
| GET | `/api/orders/<order_group>` | Get single order detail + status timeline |
| PUT | `/api/orders/<order_group>/items` | Update item quantities |
| DELETE | `/api/orders/<order_group>` | Cancel order |
| GET | `/api/debts?username=X` | Get user's debt records |
| POST | `/api/debts/pay` | Record a debt payment |
| GET | `/api/payment-accounts` | Get available payment accounts |
| POST | `/api/feedback` | Submit feedback |
| POST | `/api/contact` | Send message to admin |
| GET | `/api/help` | Get help categories and content |
| GET | `/api/notifications?user_id=X` | Get user's notifications |

### Supabase direct access (optional)
The app could also read directly from Supabase (using an anon key with RLS policies) for GET-only operations, reducing API load. Writes (orders, debt payments) go through the API to trigger admin notifications via the Telegram bot.

---

## Database Tables Used

Existing:
- `users` — user_id, full_name, username, banned
- `menu` — id, name, price, parent, available
- `orders` — id, user_id, item, qty, order_group, status, created_at
- `order_comments` — order_group, comment
- `order_payments` — order_group, payment_info
- `order_decline_reasons` — order_group, reason
- `debts` — id, username, full_name, amount, description, order_group, user_id, status
- `debt_payments` — id, username, user_id, amount, payment_info
- `debt_allow_list` — username
- `payment_accounts` — id, bank_name, number, holder_name
- `feedback` — id, user_id, name, msg, created_at

New:
- `login_otps` — id, username, user_id, otp, expires_at, used
- `notifications` — id, user_id, title, body, order_group, read, created_at

---

## Push Notifications

The backend writes to a `notifications` table. The app polls (or uses Firebase Cloud Messaging) to receive:
- Order accepted
- Order ready for pickup
- Order declined (with reason)
- Debt payment confirmed by admin
- Broadcast messages from admin

For FCM, a separate notification service (Firebase Admin SDK) would send push via the API when changes occur.

---

## Tech Stack Suggestions

| Layer | Technology |
|-------|-----------|
| Language | Kotlin |
| Architecture | MVVM + Repository pattern |
| UI | Jetpack Compose |
| Navigation | Jetpack Navigation Compose |
| Networking | Retrofit + OkHttp |
| Local storage | DataStore (session) + Room (offline cache) |
| DI | Hilt |
| Auth | Custom OTP via Telegram |
| Push | Firebase Cloud Messaging |
| Image loading | Coil |
| Min SDK | 26 (Android 8.0) |
| Target SDK | 34 (Android 14) |

---

## Security Notes

- OTP codes: 6 digits, 5-minute expiry, single-use
- API calls: rate-limited per IP (5 req/min for OTP requests)
- Supabase anon key: embedded in app, restricted by RLS policies
- No user passwords stored
- Session token: random UUID stored in EncryptedSharedPreferences
- All API calls over HTTPS

---

## Future Enhancements (v2)

- In-app chat with admin (real-time via WebSocket)
- Multiple language support (Amharic + English)
- Dark mode
- Favorites / saved items
- Order reorder (repeat last order)
- Delivery address / location sharing
- Promo codes
- In-app wallet (prepaid balance)
