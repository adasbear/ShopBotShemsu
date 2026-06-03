# Android App Authentication — Implementation Plan

---

## Goal

Users log into the Android app using their **Telegram username**. An OTP is sent to their Telegram DM via a **dedicated Pyrogram user account** (not the bot). Once verified, the app gets a session token linked to the existing `users` table — the **same database the bot uses**. Users can switch between the bot and the app freely; all data is shared.

---

## Architecture Overview

```
┌──────────────┐      ┌───────────────────┐      ┌──────────────────┐
│  Android App  │ ──►  │  Flask API        │ ──►  │  Supabase (DB)   │
│  (Kotlin)     │ ◄──  │  (Render)         │ ◄──  │                  │
└──────────────┘      │                   │      │  users           │
                      │  POST /request-otp │      │  login_otps      │
                      │  POST /verify-otp  │      │  orders          │
                      │  GET  /session     │      │  menu            │
                      └───────┬───────────┘      │  debts           │
                              │                   │  ...             │
                              │ Pyrogram Client   └──────────────────┘
                              │ (dedicated account)
                              │ sends OTP via DM
                              ▼
                    ┌──────────────────┐
                    │  User's Telegram │
                    │  DM              │
                    └──────────────────┘
```

### Key principle
- **One database.** The bot and the app read/write the same Supabase tables.
- **One users table.** If `@PPopa054` registered via the bot, they log into the app with the same username and see their existing orders/debts.
- **OTP sent via Pyrogram**, not the bot. The bot continues handling admin notifications.

---

## What Stays the Same

| Item | Status |
|------|--------|
| Supabase `users` table | Unchanged — app reads/writes the same rows |
| Supabase `menu` table | Unchanged |
| Supabase `orders`, `order_payments`, `order_comments` | Unchanged |
| Supabase `debts`, `debt_payments`, `debt_allow_list` | Unchanged |
| Supabase `payment_accounts` | Unchanged |
| Supabase `feedback` | Unchanged |
| Bot admin notifications | Unchanged — bot still notifies admin on new orders/payments |
| Bot running on Render | Unchanged — polling mode, Flask health endpoint |
| `config.py` | Same `BOT_TOKEN`, `SUPABASE_URL`, `SUPABASE_KEY`, admin info |

---

## What Changes / Gets Added

### 1. New Database Table: `login_otps`

```sql
CREATE TABLE IF NOT EXISTS login_otps (
  id SERIAL PRIMARY KEY,
  username TEXT NOT NULL,
  user_id BIGINT,
  otp TEXT NOT NULL,
  expires_at TIMESTAMPTZ NOT NULL,
  used BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 2. New Database Table: `sessions`

```sql
CREATE TABLE IF NOT EXISTS sessions (
  token UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id BIGINT NOT NULL REFERENCES users(user_id),
  username TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '30 days')
);
```

### 3. New Config Values (for Pyrogram)

```
# In config.py or .env
PYRO_API_ID = 1234567           # from my.telegram.org
PYRO_API_HASH = "your_hash_here"
PYRO_PHONE = "+251912345678"    # dedicated SIM phone number
PYRO_SESSION = ""               # will be auto-generated on first run, stored as env var
```

These go in `config.py`:
```python
PYRO_API_ID = int(os.getenv("PYRO_API_ID", 0))
PYRO_API_HASH = os.getenv("PYRO_API_HASH", "")
PYRO_PHONE = os.getenv("PYRO_PHONE", "")
```

### 4. New File: `otp_sender.py`

Handles Pyrogram client lifecycle and OTP sending.

```python
# otp_sender.py
#
# Responsibilities:
# 1. Initialize Pyrogram client with StringSession (survives Render restarts)
# 2. Keep client alive (daemon thread, like the bot)
# 3. Expose async function send_otp(username, otp_code)
# 4. Handle rate limiting (max 3 OTPs per user per hour)
# 5. Handle errors (user not found, account banned, etc.)
#
# Session persistence on Render:
# - First run: authenticate with phone number + code → get session string
# - Store session string in env var PYRO_SESSION_STRING on Render dashboard
# - Subsequent runs: load session string from env → no re-auth needed
```

**Why Pyrogram, not python-telegram-bot:**
- Bots cannot initiate conversations with users who haven't messaged them first.
- A personal Telegram account (via MTProto/Pyrogram) CAN send DMs to anyone.
- We use a **brand new, dedicated SIM number** (not the admin's personal account) to avoid ban risk.

### 5. New API Endpoints (in Flask, same as `main.py`)

Add these to the existing Flask app:

```
POST /api/auth/request-otp
  Request:  { "username": "PPopa054" }
  Action:   lookup user in `users` table → generate 6-digit OTP →
            store in `login_otps` → send via Pyrogram to user's Telegram DM
  Response: { "success": true, "message": "OTP sent" }
  Errors:   404 (user not found), 429 (rate limited)

POST /api/auth/verify-otp
  Request:  { "username": "PPopa054", "otp": "483921" }
  Action:   check `login_otps` for matching unexpired OTP →
            mark used → create `sessions` row → return token
  Response: { "success": true, "session_token": "uuid-here" }
  Errors:   401 (invalid/expired OTP)

GET /api/auth/session?token=uuid
  Action:   look up `sessions` table → return user info
  Response: { "user_id": 123, "username": "PPopa054", "full_name": "Adil" }
  Errors:   401 (invalid/expired session)
```

### 6. New Standalone Handler in main.py (for Pyrogram Thread)

```python
# In main.py, alongside the existing bot thread

async def _run_pyrogram():
    from otp_sender import init_pyro_client
    client = await init_pyro_client()
    await client.run_until_disconnected()  # keeps alive

def _start_pyro():
    asyncio.run(_run_pyrogram())

threading.Thread(target=_start_pyro, daemon=True).start()
```

### 7. Install New Dependency

```
pip install pyrogram tgcrypto
```

Add to `requirements.txt`:
```
pyrogram==2.0.106
tgcrypto==1.2.5
```

---

## Flow: User Logs into Android App

```
Step 1: User opens app → Login screen
         Enters Telegram username: "PPopa054"

Step 2: App → POST /api/auth/request-otp
                { "username": "PPopa054" }

Step 3: Flask checks `users` table:
         SELECT user_id FROM users WHERE username = 'PPopa054';
         → Found: user_id = 7041035485

Step 4: Flask generates OTP: "483921"
         INSERT INTO login_otps (username, user_id, otp, expires_at)
         VALUES ('PPopa054', 7041035485, '483921', NOW() + 5min)

Step 5: Flask → Pyrogram client → sends DM to @PPopa054:
         "Your Shemsu Shop login code: 483921
          Expires in 5 minutes."

Step 6: User reads OTP in Telegram → types into app

Step 7: App → POST /api/auth/verify-otp
                { "username": "PPopa054", "otp": "483921" }

Step 8: Flask checks:
         SELECT * FROM login_otps
         WHERE username = 'PPopa054'
           AND otp = '483921'
           AND used = FALSE
           AND expires_at > NOW();
         → Match found

Step 9: Flask marks OTP used:
         UPDATE login_otps SET used = TRUE WHERE id = X

Step 10: Flask creates session:
          INSERT INTO sessions (user_id, username)
          VALUES (7041035485, 'PPopa054');
          Returns: { "session_token": "a1b2c3d4-..." }

Step 11: App stores session_token in EncryptedSharedPreferences

Step 12: App navigates to Home screen
         All subsequent API calls include session_token in header
```

---

## How the App Uses the Same Data as the Bot

### Reading menu
```
BOT:   get_menu() → SELECT name, price FROM menu
APP:   GET /api/menu → SELECT name, price, parent FROM menu
Same table, same data.
```

### Placing an order
```
BOT:   save_order(user_id, item, qty, order_group) → INSERT INTO orders
APP:   POST /api/orders → INSERT INTO orders (same table)
Same table, same data.
```

### Viewing orders
```
BOT:   get_user_grouped_orders(user_id) → SELECT from orders
APP:   GET /api/orders?user_id=X → SELECT from orders (same)
```

### Debt
```
BOT:   get_user_debts(username) → SELECT from debts
APP:   GET /api/debts?username=X → SELECT from debts (same)
```

### What happens when admin accepts an order placed from the app?
```
Admin clicks Accept in bot → update_order_status(order_group, "Accepted")
Both the bot user and the app user see the status change.
No duplication. No sync needed. It's the same row.
```

---

## Rate Limiting Strategy

To avoid getting the Pyrogram account banned:

| Limit | Value |
|-------|-------|
| OTPs per username per hour | 3 |
| OTPs per IP per minute | 5 |
| OTP expiry | 5 minutes |
| Cooldown between resends | 60 seconds |

Implemented in Flask:
```sql
-- Count OTPs for this username in last hour
SELECT COUNT(*) FROM login_otps
WHERE username = 'PPopa054'
  AND created_at > NOW() - INTERVAL '1 hour';
-- If >= 3, return 429
```

---

## Pyrogram Session Persistence on Render

**Problem:** Render's filesystem is ephemeral — the `.session` file disappears on restart.

**Solution:** Use Pyrogram's `StringSession`.

1. **First run** (locally or with debug enabled):
   ```python
   from pyrogram import Client
   from pyrogram.session import StringSession
   
   async with Client(
       StringSession(),
       api_id=API_ID,
       api_hash=API_HASH,
       phone_number=PYRO_PHONE
   ) as app:
       session_str = await app.export_session_string()
       print(session_str)  # Copy this
   ```

2. **Paste the session string** as Render env var `PYRO_SESSION_STRING`.

3. **All subsequent runs** (on Render):
   ```python
   from pyrogram import Client
   from pyrogram.session import StringSession
   
   app = Client(
       StringSession(os.getenv("PYRO_SESSION_STRING")),
       api_id=API_ID,
       api_hash=API_HASH
   )
   ```

No re-authentication needed. The session string is a portable text representation of the login session.

---

## Dedicated SIM / Phone Number

- **DO NOT use the admin's personal number** (`@PPopa054`).
- Buy a cheap dedicated SIM (e.g., Safaricom, Ethio Telecom) — one-time cost ~50 Birr.
- Register a new Telegram account with that number.
- Add the number to your Telegram contacts so messages don't appear as "spam" from strangers.
- Set the account's username to something like `@ShemsuShopVerify`.
- This account does NOTHING except send OTPs.

---

## Implementation Order

| Step | What | Who |
|------|------|-----|
| 1 | Buy dedicated SIM → register new Telegram account → get API_ID/API_HASH from my.telegram.org | User |
| 2 | Add `login_otps` and `sessions` tables to Supabase | User (run SQL) |
| 3 | Create `otp_sender.py` with Pyrogram client and `send_otp()` function | Developer |
| 4 | Add API endpoints (`/request-otp`, `/verify-otp`, `/session`) to Flask in `main.py` | Developer |
| 5 | Generate StringSession (run locally) → paste as Render env var | User |
| 6 | Add `PYRO_API_ID`, `PYRO_API_HASH`, `PYRO_PHONE` to Render env vars | User |
| 7 | Deploy and test: request OTP → receive in Telegram → verify | User |
| 8 | Android app implements login screen using these endpoints | App dev |
| 9 | Android app implements all other screens using Supabase reads / API writes | App dev |

---

## Files to Create

```
DeliveryBot/
  otp_sender.py          ← NEW: Pyrogram client + send function
  app-auth-plan.md       ← THIS FILE (plan)
```

## Files to Modify

```
DeliveryBot/
  config.py              ← Add PYRO_API_ID, PYRO_API_HASH, PYRO_PHONE
  main.py                ← Add Flask routes, Pyrogram thread, rate limiting
  requirements.txt       ← Add pyrogram, tgcrypto
```

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Telegram bans the Pyrogram account | No OTP delivery | Use dedicated SIM; rate-limit aggressively; keep bot-based fallback |
| Render restart loses Pyrogram connection | OTP delay | Use `StringSession` — reconnects instantly; auto-retry on failure |
| User hasn't messaged the bot first | OTP still delivered (Pyrogram can DM anyone) | No issue — Pyrogram uses MTProto, not Bot API |
| OTP intercepted | Account hijack | OTP valid 5 min only; single-use; rate-limited |
| User doesn't have Telegram username set | Cannot receive OTP | App shows error: "Set a Telegram username first in Settings" |
| User is banned in `users` table | Login rejected | Flask checks `banned` flag before sending OTP |
