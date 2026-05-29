from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler

from config import ADMIN_USERNAME, ADMIN_BROADCAST, ADMIN_ADD_ITEM_NAME, ADMIN_ADD_ITEM_PRICE
from database import (
    get_all_users_detailed, ban_user, unban_user,
    get_menu, add_menu_item, delete_menu_item,
    get_pending_summary, get_pending_orders_with_users,
    get_pending_user_ids, mark_all_arrived, mark_order_arrived,
    get_all_feedback, get_all_users,
    get_grouped_orders_by_status, update_order_status,
    get_todays_profit, register_user as db_register_user
)
from keyboards import (
    get_admin_keyboard, get_admin_orders_keyboard,
    admin_menu_edit_keyboard, admin_users_keyboard,
    admin_user_action_keyboard, delivered_keyboard,
    order_accept_decline_keyboard, order_ready_keyboard,
    order_deliver_keyboard
)
from utils.helpers import is_admin, BAN_MESSAGE

def _check(update):
    return is_admin(update.effective_user.username)

def _format_items(item_list, menu):
    lines = []
    total = 0
    for it in item_list:
        price = menu.get(it["item"], 0)
        cost = it["qty"] * price
        total += cost
        lines.append(f"{it['qty']}x {it['item']} (${cost:.2f})")
    return lines, total

# --- Portal entry ---

async def show_admin_portal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _check(update):
        return ConversationHandler.END
    await db_register_user(
        update.effective_user.id,
        update.effective_user.full_name or "Admin",
        update.effective_user.username
    )
    await update.message.reply_text(
        "<b>Admin Portal</b>\n\nManage your bot from here.",
        reply_markup=get_admin_keyboard(),
        parse_mode=ParseMode.HTML
    )
    return ConversationHandler.END

# --- Users ---

async def admin_show_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _check(update):
        return ConversationHandler.END
    users = await get_all_users_detailed()
    if not users:
        await update.message.reply_text("No users registered yet.", reply_markup=get_admin_keyboard())
        return ConversationHandler.END
    await update.message.reply_text(
        f"<b>Users ({len(users)})</b>\n\nSelect a user:",
        reply_markup=await admin_users_keyboard(),
        parse_mode=ParseMode.HTML
    )
    return ConversationHandler.END

# --- Menu ---

async def admin_show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _check(update):
        return ConversationHandler.END
    menu = await get_menu()
    if not menu:
        txt = "Menu is empty."
    else:
        txt = "<b>Menu</b>\n\n"
        for name, price in menu.items():
            txt += f"{name} - ${price}\n"
    await update.message.reply_text(
        txt,
        reply_markup=await admin_menu_edit_keyboard(),
        parse_mode=ParseMode.HTML
    )
    return ConversationHandler.END

# --- Orders ---

async def admin_show_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _check(update):
        return ConversationHandler.END
    await update.message.reply_text(
        "<b>Orders</b>\n\nChoose an action:",
        reply_markup=get_admin_orders_keyboard(),
        parse_mode=ParseMode.HTML
    )
    return ConversationHandler.END

async def admin_show_new_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _check(update):
        return ConversationHandler.END
    groups = await get_grouped_orders_by_status("Pending")
    if not groups:
        await update.message.reply_text("No new orders.", reply_markup=get_admin_orders_keyboard())
        return ConversationHandler.END
    menu = await get_menu()
    msg = f"<b>New Orders ({len(groups)})</b>\n\n"
    for g in groups:
        lines, total = _format_items(g["items"], menu)
        msg += f"<b>{g['full_name']}</b>\n" + "\n".join(lines) + f"\nTotal: ${total:.2f}\n\n"
    await update.message.reply_text(msg.strip(), parse_mode=ParseMode.HTML)
    for g in groups:
        lines, total = _format_items(g["items"], menu)
        text = f"<b>{g['full_name']}</b>\n" + "\n".join(lines) + f"\nTotal: ${total:.2f}"
        await context.bot.send_message(
            update.effective_user.id,
            text,
            reply_markup=order_accept_decline_keyboard(g["order_group"]),
            parse_mode=ParseMode.HTML
        )
    return ConversationHandler.END

async def admin_show_accepted(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _check(update):
        return ConversationHandler.END
    groups = await get_grouped_orders_by_status("Accepted")
    if not groups:
        await update.message.reply_text("No accepted orders.", reply_markup=get_admin_orders_keyboard())
        return ConversationHandler.END
    menu = await get_menu()
    for g in groups:
        lines, total = _format_items(g["items"], menu)
        text = f"<b>{g['full_name']}</b>\n" + "\n".join(lines) + f"\nTotal: ${total:.2f}"
        await context.bot.send_message(
            update.effective_user.id,
            text,
            reply_markup=order_ready_keyboard(g["order_group"]),
            parse_mode=ParseMode.HTML
        )
    return ConversationHandler.END

async def admin_show_ready(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _check(update):
        return ConversationHandler.END
    groups = await get_grouped_orders_by_status("Ready")
    if not groups:
        await update.message.reply_text("No ready orders.", reply_markup=get_admin_orders_keyboard())
        return ConversationHandler.END
    menu = await get_menu()
    for g in groups:
        lines, total = _format_items(g["items"], menu)
        text = f"<b>{g['full_name']}</b>\n" + "\n".join(lines) + f"\nTotal: ${total:.2f}"
        await context.bot.send_message(
            update.effective_user.id,
            text,
            reply_markup=order_deliver_keyboard(g["order_group"]),
            parse_mode=ParseMode.HTML
        )
    return ConversationHandler.END

async def admin_show_profit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _check(update):
        return ConversationHandler.END
    profit = await get_todays_profit()
    await update.message.reply_text(
        f"<b>Today's Profit</b>\n\nTotal: ${profit:.2f}",
        reply_markup=get_admin_orders_keyboard(),
        parse_mode=ParseMode.HTML
    )
    return ConversationHandler.END

# --- Old order views (kept for backward compat) ---

async def admin_show_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _check(update):
        return ConversationHandler.END
    rows = await get_pending_summary()
    if not rows:
        msg = "No pending orders."
    else:
        msg = "<b>Pending Summary</b>\n\n"
        for r in rows:
            msg += f"{r['item']}: {r['total']}\n"
    await update.message.reply_text(msg, reply_markup=get_admin_orders_keyboard(), parse_mode=ParseMode.HTML)
    return ConversationHandler.END

async def admin_show_individual(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _check(update):
        return ConversationHandler.END
    orders = await get_pending_orders_with_users()
    if not orders:
        await update.message.reply_text("No pending orders.", reply_markup=get_admin_orders_keyboard())
        return ConversationHandler.END
    await update.message.reply_text("Pending orders (tap to mark delivered):", reply_markup=get_admin_orders_keyboard())
    for oid, name, item, qty, _ in orders:
        await context.bot.send_message(
            update.effective_user.id,
            f"{name}\n{qty}x {item}",
            reply_markup=delivered_keyboard(oid),
            parse_mode=ParseMode.HTML
        )
    return ConversationHandler.END

async def admin_mark_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _check(update):
        return ConversationHandler.END
    users = await get_pending_user_ids()
    await mark_all_arrived()
    for (uid,) in users:
        try:
            await context.bot.send_message(
                uid, "Your order has arrived! Come and get it!", parse_mode=ParseMode.HTML
            )
        except:
            pass
    await update.message.reply_text("All orders marked arrived. Users notified.", reply_markup=get_admin_orders_keyboard())
    return ConversationHandler.END

# --- Feedback ---

async def admin_show_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _check(update):
        return ConversationHandler.END
    feedback = await get_all_feedback()
    if not feedback:
        await update.message.reply_text("No feedback yet.", reply_markup=get_admin_keyboard())
        return ConversationHandler.END
    msg = "<b>Recent Feedback</b>\n\n"
    for f in feedback[:5]:
        msg += f"<b>{f['name']}</b>: {f['msg'][:100]}\n"
    if len(feedback) > 5:
        msg += f"\n... and {len(feedback) - 5} more"
    await update.message.reply_text(msg, reply_markup=get_admin_keyboard(), parse_mode=ParseMode.HTML)
    return ConversationHandler.END

# --- Broadcast ---

async def admin_start_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _check(update):
        return ConversationHandler.END
    await update.message.reply_text("Enter the <b>broadcast message</b> to send to all users:", parse_mode=ParseMode.HTML)
    return ADMIN_BROADCAST

async def admin_do_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _check(update):
        return ConversationHandler.END
    msg = update.message.text
    users = await get_all_users()
    count = 0
    for (uid,) in users:
        try:
            await context.bot.send_message(uid, f"ANNOUNCEMENT\n\n{msg}", parse_mode=ParseMode.HTML)
            count += 1
        except:
            continue
    await update.message.reply_text(f"Broadcast sent to {count} users.", reply_markup=get_admin_keyboard())
    return ConversationHandler.END

# --- Add Menu Item Flow ---

async def admin_add_item_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _check(update):
        return ConversationHandler.END
    await update.message.reply_text("Enter the <b>name</b> of the new item:", parse_mode=ParseMode.HTML)
    return ADMIN_ADD_ITEM_NAME

async def admin_add_item_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _check(update):
        return ConversationHandler.END
    context.user_data["admin_new_item"] = update.message.text
    await update.message.reply_text(f"Enter the <b>price</b> for {update.message.text} (e.g. 5.50):", parse_mode=ParseMode.HTML)
    return ADMIN_ADD_ITEM_PRICE

async def admin_add_item_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _check(update):
        return ConversationHandler.END
    try:
        price = float(update.message.text)
        name = context.user_data["admin_new_item"]
        await add_menu_item(name, price)
        await update.message.reply_text(f"Added {name} at ${price:.2f}!", reply_markup=get_admin_keyboard())
    except:
        await update.message.reply_text("Invalid price. Item not added.", reply_markup=get_admin_keyboard())
    return ConversationHandler.END

# --- Back to Portal ---

async def admin_back_to_portal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _check(update):
        return ConversationHandler.END
    await update.message.reply_text(
        "<b>Admin Portal</b>",
        reply_markup=get_admin_keyboard(),
        parse_mode=ParseMode.HTML
    )
    return ConversationHandler.END

# --- Inline Callback Handler ---

async def admin_inline_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not _check(update):
        return ConversationHandler.END

    data = query.data

    # --- Order management callbacks ---

    if data.startswith("ord_accept_") or data.startswith("ord_decline_"):
        parts = data.split("_", 2)
        action = parts[1]
        order_group = parts[2]
        menu = await get_menu()

        if action == "accept":
            await update_order_status(order_group, "Accepted")
            groups = await get_grouped_orders_by_status("Accepted")
            target = next((g for g in groups if g["order_group"] == order_group), None)
            if target:
                try:
                    lines, total = _format_items(target["items"], menu)
                    text = (
                        f"<b>Order Accepted!</b>\n\n"
                        + "\n".join(lines)
                        + f"\n\nTotal: ${total:.2f}\n\nYour order is being prepared."
                    )
                    await context.bot.send_message(target["user_id"], text, parse_mode=ParseMode.HTML)
                except:
                    pass
            await query.edit_message_text(
                f"Order accepted.",
                reply_markup=order_ready_keyboard(order_group)
            )
        else:
            await update_order_status(order_group, "Cancelled")
            groups_before = await get_grouped_orders_by_status("Pending")
            target = next((g for g in groups_before if g["order_group"] == order_group), None)
            if not target:
                groups_cancelled = await get_grouped_orders_by_status("Cancelled")
                target = next((g for g in groups_cancelled if g["order_group"] == order_group), None)
            if target:
                try:
                    await context.bot.send_message(
                        target["user_id"],
                        "<b>Order Declined</b>\n\nSorry, your order has been declined. Contact admin for details.",
                        parse_mode=ParseMode.HTML
                    )
                except:
                    pass
            await query.edit_message_text("Order declined.")
        return ConversationHandler.END

    if data.startswith("ord_ready_"):
        order_group = data.split("_", 2)[2]
        await update_order_status(order_group, "Ready")
        groups = await get_grouped_orders_by_status("Ready")
        target = next((g for g in groups if g["order_group"] == order_group), None)
        if target:
            try:
                await context.bot.send_message(
                    target["user_id"],
                    "<b>Order Ready for Pickup!</b>\n\nYour order is ready. Please come and pick it up.",
                    parse_mode=ParseMode.HTML
                )
            except:
                pass
        await query.edit_message_text(
            "Marked as ready.",
            reply_markup=order_deliver_keyboard(order_group)
        )
        return ConversationHandler.END

    if data.startswith("ord_deliver_"):
        order_group = data.split("_", 2)[2]
        await update_order_status(order_group, "Delivered")
        groups = await get_grouped_orders_by_status("Delivered")
        target = next((g for g in groups if g["order_group"] == order_group), None)
        if target:
            try:
                await context.bot.send_message(
                    target["user_id"],
                    "<b>Order Delivered!</b>\n\nThank you for your order! Come back soon.",
                    parse_mode=ParseMode.HTML
                )
            except:
                pass
        await query.edit_message_text("Order delivered.")
        user = context.user_data.get("admin_selected_user", {})
        return ConversationHandler.END

    # --- User management ---

    if data.startswith("auser_"):
        target_id = int(data.split("_", 1)[1])
        users = await get_all_users_detailed()
        user = next((u for u in users if u["user_id"] == target_id), None)
        if not user:
            await query.edit_message_text("User not found.")
            return ConversationHandler.END
        context.user_data["admin_selected_user"] = user
        await query.edit_message_text(
            f"<b>{user['full_name']}</b> (@{user['username'] or 'no username'})",
            reply_markup=admin_user_action_keyboard(target_id, user["banned"]),
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END

    if data.startswith("aban_") or data.startswith("aunban_"):
        parts = data.split("_", 1)
        target_id = int(parts[1])
        if parts[0] == "aban":
            await ban_user(target_id)
            is_banned = True
            try:
                await context.bot.send_message(
                    target_id, BAN_MESSAGE,
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("Contact Admin", callback_data="contact_admin")
                    ]]),
                    parse_mode=ParseMode.HTML
                )
            except:
                pass
        else:
            await unban_user(target_id)
            is_banned = False
            try:
                await context.bot.send_message(
                    target_id,
                    "<b>You have been unbanned</b>\n\nYou can now use the bot again.",
                    parse_mode=ParseMode.HTML
                )
            except:
                pass
        user = context.user_data.get("admin_selected_user", {})
        name = user.get("full_name", "User")
        await query.edit_message_text(
            f"<b>{name}</b>\n\nStatus: {'Banned' if is_banned else 'Active'}",
            reply_markup=admin_user_action_keyboard(target_id, is_banned),
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END

    if data == "aback_users":
        users = await get_all_users_detailed()
        await query.edit_message_text(
            f"<b>Users ({len(users)})</b>\n\nSelect a user:",
            reply_markup=await admin_users_keyboard(),
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END

    # --- Menu management ---

    if data.startswith("adel_"):
        name = data.replace("adel_", "")
        await delete_menu_item(name)
        await query.edit_message_text(
            f"Deleted {name}.", reply_markup=await admin_menu_edit_keyboard(),
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END

    if data == "admin_add_item":
        await query.edit_message_text("Enter the <b>name</b> of the new item:", parse_mode=ParseMode.HTML)
        return ADMIN_ADD_ITEM_NAME

    # --- Legacy deliver (per-item, backward compat) ---

    if data.startswith("deliver_"):
        order_id = int(data.replace("deliver_", ""))
        order = await mark_order_arrived(order_id)
        if order:
            uid, item, qty = order
            try:
                await context.bot.send_message(
                    uid, f"Order Arrived!\nYour {qty}x {item} is ready!", parse_mode=ParseMode.HTML
                )
            except:
                pass
            await query.edit_message_text(f"Delivered: {qty}x {item}.")
        return ConversationHandler.END

    return ConversationHandler.END
