import asyncio
from datetime import datetime, timezone
from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY

_supabase = None

def init_db():
    global _supabase
    _supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

async def _db(callable):
    return await asyncio.to_thread(callable)

# --- Users ---

async def get_user(user_id):
    result = await _db(lambda: _supabase.table("users").select("full_name, banned").eq("user_id", user_id).execute())
    if result.data:
        return result.data[0]
    return None

async def register_user(user_id, full_name, username):
    await _db(lambda: _supabase.table("users").upsert({
        "user_id": user_id,
        "full_name": full_name,
        "username": username,
        "banned": False
    }).execute())

async def get_all_users_detailed():
    result = await _db(lambda: _supabase.table("users").select("user_id, full_name, username, banned").order("full_name").execute())
    return result.data

async def ban_user(user_id):
    await _db(lambda: _supabase.table("users").update({"banned": True}).eq("user_id", user_id).execute())

async def unban_user(user_id):
    await _db(lambda: _supabase.table("users").update({"banned": False}).eq("user_id", user_id).execute())

async def get_all_users():
    result = await _db(lambda: _supabase.table("users").select("user_id").execute())
    return [(r["user_id"],) for r in result.data]

async def get_admin_user_id():
    result = await _db(lambda: _supabase.table("users").select("user_id").eq("username", "Barc_h").execute())
    if result.data:
        return result.data[0]["user_id"]
    from config import ADMIN_USER_ID
    if ADMIN_USER_ID:
        return ADMIN_USER_ID
    return None

# --- Menu ---

async def get_menu():
    result = await _db(lambda: _supabase.table("menu").select("name, price").execute())
    return {row["name"]: row["price"] for row in result.data}

async def delete_menu_item(name):
    await _db(lambda: _supabase.table("menu").delete().eq("name", name).execute())

async def add_menu_item(name, price):
    await _db(lambda: _supabase.table("menu").upsert({
        "name": name, "price": price
    }).execute())

# --- Orders ---

async def save_order(user_id, item, qty, order_group, status="Pending"):
    await _db(lambda: _supabase.table("orders").insert({
        "user_id": user_id,
        "item": item,
        "qty": qty,
        "status": status,
        "order_group": order_group,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }).execute())

async def update_order_status(order_group, new_status):
    await _db(lambda: _supabase.table("orders").update({"status": new_status}).eq("order_group", order_group).execute())

async def get_grouped_orders_by_status(status):
    result = await _db(lambda: _supabase.table("orders")
        .select("id, user_id, item, qty, order_group, users(full_name)")
        .eq("status", status)
        .execute())
    groups = {}
    for r in result.data:
        g = r["order_group"]
        if not g:
            continue
        if g not in groups:
            groups[g] = {
                "order_group": g,
                "user_id": r["user_id"],
                "full_name": r["users"]["full_name"],
                "items": []
            }
        groups[g]["items"].append({"item": r["item"], "qty": r["qty"]})
    return list(groups.values())

async def get_pending_summary():
    result = await _db(lambda: _supabase.table("orders").select("item, qty").eq("status", "Pending").execute())
    summary = {}
    for row in result.data:
        summary[row["item"]] = summary.get(row["item"], 0) + row["qty"]
    return [{"item": k, "total": v} for k, v in summary.items()]

async def get_pending_orders_with_users():
    result = await _db(lambda: _supabase.table("orders").select("id, item, qty, order_group, users(full_name)").eq("status", "Pending").execute())
    return [(r["id"], r["users"]["full_name"], r["item"], r["qty"], r.get("order_group")) for r in result.data]

async def get_pending_user_ids():
    result = await _db(lambda: _supabase.table("orders").select("user_id").eq("status", "Pending").execute())
    seen = set()
    unique = []
    for r in result.data:
        uid = r["user_id"]
        if uid not in seen:
            seen.add(uid)
            unique.append((uid,))
    return unique

async def mark_all_arrived():
    await _db(lambda: _supabase.table("orders").update({"status": "Arrived"}).eq("status", "Pending").execute())

async def mark_order_arrived(order_id):
    result = await _db(lambda: _supabase.table("orders").select("user_id, item, qty").eq("id", order_id).execute())
    if not result.data:
        return None
    row = result.data[0]
    await _db(lambda: _supabase.table("orders").update({"status": "Arrived"}).eq("id", order_id).execute())
    return (row["user_id"], row["item"], row["qty"])

async def get_user_orders(user_id, limit=5):
    result = await _db(lambda: _supabase.table("orders")
        .select("item, qty, status")
        .eq("user_id", user_id)
        .order("timestamp", desc=True)
        .limit(limit)
        .execute())
    return [(r["item"], r["qty"], r["status"]) for r in result.data]

async def get_todays_profit():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    result = await _db(lambda: _supabase.table("orders")
        .select("item, qty")
        .eq("status", "Delivered")
        .gte("timestamp", today)
        .execute())
    menu = await get_menu()
    total = sum(row["qty"] * menu.get(row["item"], 0) for row in result.data)
    return total

# --- Feedback ---

async def save_feedback(user_id, msg):
    name_result = await _db(lambda: _supabase.table("users").select("full_name").eq("user_id", user_id).execute())
    name = name_result.data[0]["full_name"] if name_result.data else "Unknown"
    await _db(lambda: _supabase.table("feedback").insert({
        "user_id": user_id, "name": name, "msg": msg
    }).execute())

async def get_all_feedback():
    result = await _db(lambda: _supabase.table("feedback")
        .select("id, user_id, name, msg, created_at")
        .order("created_at", desc=True)
        .execute())
    return result.data
