import urllib.request, json

base = "https://shopbotshemsu-1.onrender.com"

# Test menu
try:
    req = urllib.request.Request(base + "/api/menu")
    resp = urllib.request.urlopen(req, timeout=15)
    data = json.loads(resp.read().decode())
    print(f"Menu: OK, {len(data)} items")
    for item in data[:3]:
        print(f"  {item}")
except Exception as e:
    print(f"Menu FAILED: {e}")

# Test notifications
try:
    req = urllib.request.Request(base + "/api/notifications?user_id=7041035485")
    resp = urllib.request.urlopen(req, timeout=15)
    data = json.loads(resp.read().decode())
    print(f"Notifications: OK, {len(data)} items")
except Exception as e:
    print(f"Notifications FAILED: {e}")

# Test debts
try:
    req = urllib.request.Request(base + "/api/debts?username=PPopa054")
    resp = urllib.request.urlopen(req, timeout=15)
    data = json.loads(resp.read().decode())
    is_list = isinstance(data, list)
    print(f"Debts: OK, type={'list' if is_list else 'dict'}, count={len(data) if is_list else len(data.get('records', []))}")
except Exception as e:
    print(f"Debts FAILED: {e}")

# Test active total
try:
    req = urllib.request.Request(base + "/api/debts/active-total?username=PPopa054")
    resp = urllib.request.urlopen(req, timeout=15)
    data = json.loads(resp.read().decode())
    print(f"Debts active-total: OK, {data}")
except Exception as e:
    print(f"Debts active-total FAILED: {e}")

# Test payment accounts
try:
    req = urllib.request.Request(base + "/api/payment-accounts")
    resp = urllib.request.urlopen(req, timeout=15)
    data = json.loads(resp.read().decode())
    print(f"Payment accounts: OK, {len(data)} accounts")
except Exception as e:
    print(f"Payment accounts FAILED: {e}")

# Test debt allow list check
try:
    req = urllib.request.Request(base + "/api/debt-allow-list/check?username=PPopa054")
    resp = urllib.request.urlopen(req, timeout=15)
    data = json.loads(resp.read().decode())
    print(f"Debt allow-list: OK, {data}")
except Exception as e:
    print(f"Debt allow-list FAILED: {e}")
