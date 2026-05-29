from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

def get_main_keyboard():
    buttons = [["Menu", "Profile"], ["My Orders", "Feedback"], ["Commands"]]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

async def menu_inline_keyboard():
    from database import get_menu
    menu = await get_menu()
    kb = [[InlineKeyboardButton(f"{k} - ${v}", callback_data=f"order_{k}")] for k, v in menu.items()]
    return InlineKeyboardMarkup(kb)

def add_more_or_review_keyboard(total):
    kb = [
        [InlineKeyboardButton("Add More", callback_data="add_more")],
        [InlineKeyboardButton(f"Review Order (${total:.2f})", callback_data="review")]
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

def delivered_keyboard(order_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Delivered", callback_data=f"deliver_{order_id}")]
    ])

def get_admin_keyboard():
    buttons = [
        ["Users", "Manage Menu", "Orders"],
        ["Feedback", "Broadcast"]
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

def get_admin_orders_keyboard():
    buttons = [
        ["Summary", "Mark Delivered", "Mark All Arrived"],
        ["Back to Portal"]
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

async def admin_menu_edit_keyboard():
    from database import get_menu
    menu = await get_menu()
    kb = []
    for name in menu:
        kb.append([InlineKeyboardButton(f"Delete {name}", callback_data=f"adel_{name}")])
    kb.append([InlineKeyboardButton("Add Item", callback_data="admin_add_item")])
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
