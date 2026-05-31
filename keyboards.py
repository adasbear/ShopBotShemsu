from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

def get_main_keyboard():
    buttons = [["Menu", "Profile"], ["My Orders", "Feedback"], ["Help", "Refresh"], ["My Debt"]]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

async def menu_inline_keyboard(show_back=True, parent=None):
    from database import get_top_level_menu, get_sub_menu, has_sub_items
    if parent:
        menu = await get_sub_menu(parent)
    else:
        menu = await get_top_level_menu()
    kb = []
    for k, v in menu.items():
        is_cat = await has_sub_items(k) if not parent else False
        label = f"{k} ▶️" if is_cat else f"{k} - Birr {v}"
        kb.append([InlineKeyboardButton(label, callback_data=f"order_{k}")])
    kb.append([InlineKeyboardButton("Other ✏️", callback_data="order_Other")])
    if show_back:
        back_data = "order_back_to_main" if parent else "order_back"
        kb.append([InlineKeyboardButton("⬅ Back", callback_data=back_data)])
    return InlineKeyboardMarkup(kb)

def add_more_or_review_keyboard(total):
    kb = [
        [InlineKeyboardButton("Add More", callback_data="add_more")],
        [InlineKeyboardButton(f"Review Order (Birr {total:.2f})", callback_data="review")]
    ]
    return InlineKeyboardMarkup(kb)

def comment_choice_keyboard():
    kb = [
        [InlineKeyboardButton("Add Comment ✏️", callback_data="add_comment")],
        [InlineKeyboardButton("No Thanks ✅", callback_data="skip_comment")]
    ]
    return InlineKeyboardMarkup(kb)

def confirm_cancel_keyboard():
    kb = [
        [InlineKeyboardButton("CONFIRM", callback_data="confirm")],
        [InlineKeyboardButton("CANCEL", callback_data="cancel")]
    ]
    return InlineKeyboardMarkup(kb)

def get_banned_keyboard():
    return ReplyKeyboardMarkup([["Contact Admin"]], resize_keyboard=True)

# --- Order flow inline keyboards ---

def order_accept_decline_keyboard(order_group):
    kb = [
        [InlineKeyboardButton("Accept", callback_data=f"ord_accept_{order_group}"),
         InlineKeyboardButton("Decline", callback_data=f"ord_decline_{order_group}")]
    ]
    return InlineKeyboardMarkup(kb)

def order_ready_keyboard(order_group):
    kb = [
        [InlineKeyboardButton("Ready for Pickup", callback_data=f"ord_ready_{order_group}")]
    ]
    return InlineKeyboardMarkup(kb)

def order_deliver_keyboard(order_group):
    kb = [
        [InlineKeyboardButton("Delivered", callback_data=f"ord_deliver_{order_group}")]
    ]
    return InlineKeyboardMarkup(kb)

def delivered_keyboard(order_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Delivered", callback_data=f"deliver_{order_id}")]
    ])

# --- Admin keyboards ---

def get_admin_keyboard():
    buttons = [
        ["Users", "Manage Menu", "Orders"],
        ["Debt Management", "Feedback"],
        ["Broadcast"]
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

def get_admin_orders_keyboard():
    buttons = [
        ["New Orders", "Accepted", "Ready"],
        ["Today's Profit"],
        ["Back to Portal"]
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

async def admin_menu_edit_keyboard():
    from database import get_all_menu_items, has_sub_items
    items = await get_all_menu_items()
    kb = []
    for row in items:
        name = row["name"]
        if await has_sub_items(name):
            kb.append([InlineKeyboardButton(f"Manage {name} ▶️", callback_data=f"manage_cat_{name}")])
        else:
            kb.append([InlineKeyboardButton(f"Delete {name}", callback_data=f"adel_{name}")])
    kb.append([InlineKeyboardButton("Add Item", callback_data="admin_add_item")])
    kb.append([InlineKeyboardButton("Add Category", callback_data="admin_add_category")])
    return InlineKeyboardMarkup(kb)

async def admin_category_keyboard(category):
    from database import get_sub_menu
    items = await get_sub_menu(category)
    kb = []
    for name, price in items.items():
        kb.append([InlineKeyboardButton(f"Delete {name}", callback_data=f"adel_{name}")])
    kb.append([InlineKeyboardButton("Add Sub-item", callback_data=f"add_subitem_{category}")])
    kb.append([InlineKeyboardButton("⬅ Back", callback_data="admin_back_menu")])
    return InlineKeyboardMarkup(kb)

async def admin_users_keyboard():
    from database import get_all_users_detailed
    users = await get_all_users_detailed()
    kb = []
    for u in users:
        kb.append([InlineKeyboardButton(u["full_name"], callback_data=f"auser_{u['user_id']}")])
    return InlineKeyboardMarkup(kb)

def admin_user_action_keyboard(user_id, is_banned):
    action = "Unban User" if is_banned else "Ban User"
    cb = f"aunban_{user_id}" if is_banned else f"aban_{user_id}"
    kb = [
        [InlineKeyboardButton(action, callback_data=cb)],
        [InlineKeyboardButton("Back to Users", callback_data="aback_users")]
    ]
    return InlineKeyboardMarkup(kb)

# --- Debt keyboards ---

def debt_choice_keyboard():
    kb = [
        [InlineKeyboardButton("Pay Now 💰", callback_data="pay_now")],
        [InlineKeyboardButton("Take on Debt 📋", callback_data="debt_take")],
        [InlineKeyboardButton("Cancel Order ❌", callback_data="debt_cancel")]
    ]
    return InlineKeyboardMarkup(kb)

def debt_not_allowed_keyboard():
    kb = [
        [InlineKeyboardButton("Pay Now 💰", callback_data="pay_now")],
        [InlineKeyboardButton("Cancel Order ❌", callback_data="debt_cancel")]
    ]
    return InlineKeyboardMarkup(kb)

def deliver_paid_debt_keyboard(order_group):
    kb = [
        [InlineKeyboardButton("Paid 💰", callback_data=f"ord_paid_{order_group}"),
         InlineKeyboardButton("Debt 📋", callback_data=f"ord_debt_{order_group}")]
    ]
    return InlineKeyboardMarkup(kb)

def get_admin_debt_keyboard():
    buttons = [
        ["Allow List", "All Debts"],
        ["Back to Portal"]
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

async def admin_allow_list_inline_keyboard():
    from database import get_debt_allow_list
    entries = await get_debt_allow_list()
    kb = []
    for e in entries:
        kb.append([InlineKeyboardButton(f"Remove @{e['username']}", callback_data=f"adel_allow_{e['username']}")])
    kb.append([InlineKeyboardButton("Add Username ➕", callback_data="admin_add_allow")])
    kb.append([InlineKeyboardButton("⬅ Back", callback_data="admin_back_debt")])
    return InlineKeyboardMarkup(kb)

async def admin_debts_inline_keyboard(filter_status=None):
    from database import get_all_debts
    debts = await get_all_debts(status_filter=filter_status)
    kb = []
    for d in debts[:15]:
        name = d.get("full_name", d["username"])
        label = f"{name} (@{d['username']}) - Birr {d['amount']:.2f}"
        kb.append([InlineKeyboardButton(label, callback_data=f"adebt_{d['id']}")])
    kb.append([InlineKeyboardButton("Show Active", callback_data="adebt_filter_active")])
    kb.append([InlineKeyboardButton("Show All", callback_data="adebt_filter_all")])
    kb.append([InlineKeyboardButton("⬅ Back", callback_data="admin_back_debt")])
    return InlineKeyboardMarkup(kb)

def admin_debt_action_keyboard(debt_id):
    kb = [
        [InlineKeyboardButton("Mark Paid ✅", callback_data=f"adebt_paid_{debt_id}")],
        [InlineKeyboardButton("Waive 🚫", callback_data=f"adebt_waive_{debt_id}")],
        [InlineKeyboardButton("⬅ Back", callback_data="adebt_back_to_list")]
    ]
    return InlineKeyboardMarkup(kb)
