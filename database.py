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
    from config import ADMIN_USERNAME, ADMIN_USER_ID
    result = await _db(lambda: _supabase.table("users").select("user_id").eq("username", ADMIN_USERNAME).execute())
    if result.data:
        return result.data[0]["user_id"]
    if ADMIN_USER_ID:
        return ADMIN_USER_ID
    return None

# --- Menu ---

async def get_menu():
    result = await _db(lambda: _supabase.table("menu").select("name, price").execute())
    return {row["name"]: row["price"] for row in result.data}

async def get_top_level_menu():
    result = await _db(lambda: _supabase.table("menu").select("name, price").is_("parent", "null").execute())
    return {row["name"]: row["price"] for row in result.data}

async def get_sub_menu(parent):
    result = await _db(lambda: _supabase.table("menu").select("name, price").eq("parent", parent).execute())
    return {row["name"]: row["price"] for row in result.data}

async def has_sub_items(name):
    result = await _db(lambda: _supabase.table("menu").select("name").eq("parent", name).limit(1).execute())
    return len(result.data) > 0

async def get_all_menu_items():
    result = await _db(lambda: _supabase.table("menu").select("name, price, parent").order("parent").execute())
    return result.data

async def delete_menu_item(name):
    await _db(lambda: _supabase.table("menu").delete().eq("parent", name).execute())
    await _db(lambda: _supabase.table("menu").delete().eq("name", name).execute())

async def add_menu_item(name, price, parent=None):
    data = {"name": name, "price": price}
    if parent:
        data["parent"] = parent
    await _db(lambda: _supabase.table("menu").upsert(data).execute())

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

# --- Order management (edit/cancel) ---

async def get_user_grouped_orders(user_id, limit=5):
    result = await _db(lambda: _supabase.table("orders")
        .select("id, item, qty, status, order_group, timestamp")
        .eq("user_id", user_id)
        .order("timestamp", desc=True)
        .limit(50)
        .execute())
    groups = {}
    for r in result.data:
        g = r["order_group"]
        if g not in groups:
            groups[g] = {
                "order_group": g,
                "timestamp": r["timestamp"],
                "status": r["status"],
                "items": []
            }
        groups[g]["items"].append({"id": r["id"], "item": r["item"], "qty": r["qty"]})
    sorted_groups = sorted(groups.values(), key=lambda x: x["timestamp"], reverse=True)
    return sorted_groups[:limit]

async def get_order_items(order_group):
    result = await _db(lambda: _supabase.table("orders")
        .select("id, item, qty, status, timestamp")
        .eq("order_group", order_group)
        .execute())
    return result.data

async def update_item_qty(item_id, new_qty):
    await _db(lambda: _supabase.table("orders").update({"qty": new_qty}).eq("id", item_id).execute())

async def cancel_order_group(order_group):
    await _db(lambda: _supabase.table("orders").update({"status": "Cancelled"}).eq("order_group", order_group).execute())

# --- Order Comments ---

async def save_order_comment(order_group, comment):
    await _db(lambda: _supabase.table("order_comments").upsert({
        "order_group": order_group, "comment": comment
    }).execute())

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
