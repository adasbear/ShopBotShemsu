# Deploy to PythonAnywhere

## Prerequisites

- PythonAnywhere account (free tier)
- GitHub account with the bot repo pushed
- Your PythonAnywhere username (e.g. `yourname`)

---

## Step 1 — Create a PythonAnywhere account

1. Go to https://www.pythonanywhere.com and sign up (free)
2. Note your username — you'll need it below

---

## Step 2 — Open a Bash console

1. Log into PythonAnywhere
2. Click **Dashboard** → **Bash** (opens a terminal)

---

## Step 3 — Clone your repo

In the Bash console, run:

```bash
git clone https://github.com/adasbear/ShopBotShemsu.git
cd ShopBotShemsu
```

---

## Step 4 — Create a virtualenv and install packages

```bash
mkvirtualenv --python=python3.10 botenv
pip install -r requirements.txt
```

---

## Step 5 — Set environment variables

PythonAnywhere web apps need env vars set manually. Run these commands to create a `.env` file:

```bash
echo "BOT_TOKEN=8768868555:AAFriBhP04Ib9okUIbBfBiidVd55J-LVI3o" > .env
echo "SUPABASE_URL=https://yqpmyowjomnbnvysbokv.supabase.co" >> .env
echo "SUPABASE_KEY=sb_publishable_4T5Ul7YIoU_fvW5gShZo5g_abo7ixpV" >> .env
echo "WEBHOOK_URL=https://YOURUSERNAME.pythonanywhere.com/webhook" >> .env
```

> **IMPORTANT:** Replace `YOURUSERNAME` with your actual PythonAnywhere username.

---

## Step 6 — Set up the web app

1. Go to **Dashboard** → **Web**
2. Click **Add a new web app**
3. Choose **Manual configuration** (not "Flask" — we'll point it manually)
4. Choose **Python 3.10**
5. In the **Code** section:

| Field | Value |
|-------|-------|
| Source code | `/home/YOURUSERNAME/ShopBotShemsu` |
| Working directory | `/home/YOURUSERNAME/ShopBotShemsu` |
| WSGI configuration file | Click the link, then **replace everything** with the contents of `wsgi.py` |

6. Click **Save**

To edit the WSGI file quickly, you can also run in Bash:

```bash
cp wsgi.py /var/www/YOURUSERNAME_pythonanywhere_com_wsgi.py
```

---

## Step 7 — Set the webhook with Telegram

In the Bash console, run this ONE-TIME command to tell Telegram where to send updates:

```bash
curl -X POST "https://api.telegram.org/bot8768868555:AAFriBhP04Ib9okUIbBfBiidVd55J-LVI3o/setWebhook?url=https://YOURUSERNAME.pythonanywhere.com/webhook"
```

You should get back: `{"ok": true, "result": true, "description": "Webhook was set"}`

---

## Step 8 — Reload your web app

1. Go to **Dashboard** → **Web**
2. Click the **Reload** button (green button at top)
3. Wait 10 seconds

---

## Step 9 — Check if it works

Visit: `https://YOURUSERNAME.pythonanywhere.com/health`

You should see: `ok`

Now open Telegram and test your bot. Send `/start` to it.

---

## Step 10 — Set up cron-job.org (keep it alive)

PythonAnywhere free tier goes to sleep after a while. We need a ping every 5 minutes.

1. Go to https://cron-job.org and sign up (free, no credit card)
2. Click **Create Cronjob**
3. Set:

| Field | Value |
|-------|-------|
| Title | `ShopBot health check` |
| URL | `https://YOURUSERNAME.pythonanywhere.com/health` |
| Interval | Every 5 minutes |
| Method | GET |

4. Click **Create**

The cron job will ping your bot every 5 minutes, keeping it awake.

---

## Troubleshooting

### "Bot not responding"
Check your web app logs in PythonAnywhere Dashboard → Web → **Logs** (Error log / Server log).

### Supabase connection fails on free tier
Free PythonAnywhere has restricted internet access. If Supabase isn't accessible:
1. Check the error log
2. If it fails, you need the **$10/month Developer** plan (full internet access)

### 409 Conflict error
This means another instance of the bot is still running elsewhere (like on Render or your PC).
- If Render is still running: go to Render dashboard and stop/delete the old service
- If local: close any terminal running the old `main.py`

### Webhook not set / "Wrong URL"
Make sure:
- The `.env` file has the correct `WEBHOOK_URL`
- The web app is reloaded after changing `.env`
- The curl command returned `"ok": true`

---

## Updating the bot

When you push changes to GitHub, update on PythonAnywhere:

```bash
# In the Bash console:
cd ~/ShopBotShemsu
git pull
workon botenv
pip install -r requirements.txt
# Then reload the web app from the Web tab
```

---

## Important Notes

- The bot uses **webhook mode** now (not polling). Telegram sends updates directly to your PythonAnywhere URL.
- The background thread keeps the bot "running" in memory. The cron-job keeps the web process alive.
- If you stop using PythonAnywhere, don't forget to **remove the webhook**:
  ```bash
  curl -X POST "https://api.telegram.org/bot8768868555:AAFriBhP04Ib9okUIbBfBiidVd55J-LVI3o/deleteWebhook"
  ```
