from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler

from config import ADMIN_USERNAME, ADMIN_BROADCAST, ADMIN_ADD_ITEM_NAME, ADMIN_ADD_ITEM_PRICE, ADMIN_ADD_CATEGORY, ADMIN_MANAGE_CATEGORY, ADMIN_ADD_SUBITEM_NAME, ADMIN_ADD_SUBITEM_PRICE, ADMIN_DEBT_MENU, ADMIN_PAYMENT_MENU
from database import (
    get_all_users_detailed, ban_user, unban_user,
    get_menu, add_menu_item, delete_menu_item,
    get_all_menu_items,
    get_pending_summary, get_pending_orders_with_users,
    get_pending_user_ids, mark_all_arrived, mark_order_arrived,
    get_all_feedback, get_all_users,
    get_grouped_orders_by_status, update_order_status,
    get_todays_profit, register_user as db_register_user,
    add_to_debt_allow_list, remove_from_debt_allow_list,
    get_debt_allow_list, add_debt, get_user,
    get_all_debts, mark_debt_paid, waive_debt,
    get_payment_accounts, add_payment_account, delete_payment_account
)
from keyboards import (
    get_admin_keyboard, get_admin_orders_keyboard, get_admin_debt_keyboard, get_admin_payment_keyboard,
    admin_menu_edit_keyboard, admin_category_keyboard,
    admin_users_keyboard, admin_user_action_keyboard,
    delivered_keyboard,
    order_accept_decline_keyboard, order_ready_keyboard,
    order_deliver_keyboard, deliver_paid_debt_keyboard,
    admin_allow_list_inline_keyboard, admin_debts_inline_keyboard,
    admin_debt_action_keyboard,
    admin_payment_accounts_keyboard
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
        lines.append(f"{it['qty']}x {it['item']} (Birr {cost:.2f})")
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
    items = await get_all_menu_items()
    if not items:
        txt = "Menu is empty."
    else:
        txt = "<b>Menu</b>\n\n"
        cats = [r for r in items if r["parent"] is None]
        for r in cats:
            sub = [s for s in items if s["parent"] == r["name"]]
            if sub:
                txt += f"📁 <b>{r['name']}</b>\n"
                for s in sub:
                    txt += f"   {s['name']} - Birr {s['price']}\n"
            else:
                txt += f"{r['name']} - Birr {r['price']}\n"
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
        msg += f"<b>{g['full_name']}</b>\n" + "\n".join(lines) + f"\nTotal: Birr {total:.2f}\n\n"
    await update.message.reply_text(msg.strip(), parse_mode=ParseMode.HTML)
    for g in groups:
        lines, total = _format_items(g["items"], menu)
        text = f"<b>{g['full_name']}</b>\n" + "\n".join(lines) + f"\nTotal: Birr {total:.2f}"
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
        text = f"<b>{g['full_name']}</b>\n" + "\n".join(lines) + f"\nTotal: Birr {total:.2f}"
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
        text = f"<b>{g['full_name']}</b>\n" + "\n".join(lines) + f"\nTotal: Birr {total:.2f}"
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
        f"<b>Today's Profit</b>\n\nTotal: Birr {profit:.2f}",
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

async def admin_no_item_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _check(update):
        return ConversationHandler.END
    from database import get_todays_grouped_orders, get_menu
    groups = await get_todays_grouped_orders()
    if not groups:
        await update.message.reply_text("No orders today.", reply_markup=get_admin_orders_keyboard())
        return ConversationHandler.END
    menu = await get_menu()
    msg = f"<b>Today's Orders ({len(groups)})</b>\n\nSelect one to mark item not found:"
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
    for g in groups:
        lines = [f"{i['item']} x{i['qty']}" for i in g["items"]]
        total = sum(menu.get(i["item"], 0) * i["qty"] for i in g["items"])
        text = f"<b>{g['order_group']}</b>\n" + "\n".join(lines) + f"\nTotal: Birr {total:.2f}\nStatus: {g['status']}"
        from keyboards import no_item_select_keyboard
        await context.bot.send_message(
            update.effective_user.id,
            text,
            reply_markup=no_item_select_keyboard(g["order_group"]),
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
        await update.message.reply_text(f"Added {name} at Birr {price:.2f}!", reply_markup=get_admin_keyboard())
    except:
        await update.message.reply_text("Invalid price. Item not added.", reply_markup=get_admin_keyboard())
    return ConversationHandler.END

# --- Add Category Flow ---

async def admin_add_category_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _check(update):
        return ConversationHandler.END
    await update.message.reply_text("Enter the <b>name</b> of the new category:", parse_mode=ParseMode.HTML)
    return ADMIN_ADD_CATEGORY

async def admin_add_category_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _check(update):
        return ConversationHandler.END
    name = update.message.text.strip()
    if not name:
        await update.message.reply_text("Name cannot be empty.")
        return ADMIN_ADD_CATEGORY
    await add_menu_item(name, 0.0)
    await update.message.reply_text(f"Category <b>{name}</b> added!", reply_markup=await admin_menu_edit_keyboard())
    return ConversationHandler.END

# --- Manage Category (view sub-items, add sub-item) ---

async def admin_manage_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not _check(update):
        return ConversationHandler.END
    category = query.data.replace("manage_cat_", "")
    context.user_data["manage_category"] = category
    from keyboards import admin_category_keyboard
    items = await get_sub_menu(category)
    if items:
        lines = "\n".join(f"{n} - Birr {p}" for n, p in items.items())
        txt = f"<b>{category}</b> sub-items:\n\n{lines}"
    else:
        txt = f"<b>{category}</b> has no sub-items yet."
    await query.edit_message_text(txt, reply_markup=await admin_category_keyboard(category))
    return ConversationHandler.END

# --- Add Sub-item Flow ---

async def admin_add_sub_item_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not _check(update):
        return ConversationHandler.END
    category = query.data.replace("add_subitem_", "")
    context.user_data["admin_sub_parent"] = category
    await query.edit_message_text(
        f"Enter the <b>name</b> of the sub-item under {category}:",
        parse_mode=ParseMode.HTML
    )
    return ADMIN_ADD_SUBITEM_NAME

async def admin_add_sub_item_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _check(update):
        return ConversationHandler.END
    context.user_data["admin_new_item"] = update.message.text
    await update.message.reply_text(
        f"Enter the <b>price</b> for {update.message.text}:",
        parse_mode=ParseMode.HTML
    )
    return ADMIN_ADD_SUBITEM_PRICE

async def admin_add_sub_item_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _check(update):
        return ConversationHandler.END
    try:
        price = float(update.message.text)
        name = context.user_data["admin_new_item"]
        parent = context.user_data["admin_sub_parent"]
        await add_menu_item(name, price, parent)
        await update.message.reply_text(
            f"Added {name} (Birr {price:.2f}) under {parent}!",
            reply_markup=await admin_menu_edit_keyboard()
        )
    except:
        await update.message.reply_text("Invalid price.", reply_markup=await admin_menu_edit_keyboard())
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

# --- Debt Management ---

async def admin_debt_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _check(update):
        return ConversationHandler.END
    await update.message.reply_text(
        "<b>Debt Management</b>\n\nChoose an option:",
        reply_markup=get_admin_debt_keyboard(),
        parse_mode=ParseMode.HTML
    )
    return ConversationHandler.END

async def admin_show_allow_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _check(update):
        return ConversationHandler.END
    entries = await get_debt_allow_list()
    if not entries:
        txt = "Allow list is empty.\n\nTap <b>Add Username</b> to add someone."
    else:
        txt = "<b>Debt Allow List</b>\n\n"
        for e in entries:
            txt += f"• @{e['username']}\n"
    await update.message.reply_text(
        txt,
        reply_markup=await admin_allow_list_inline_keyboard(),
        parse_mode=ParseMode.HTML
    )
    return ConversationHandler.END

async def admin_add_allow_list_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _check(update):
        return ConversationHandler.END
    context.user_data["expect_allow_username"] = True
    await update.message.reply_text(
        "Enter the Telegram <b>username</b> to allow for debt (with or without @):",
        parse_mode=ParseMode.HTML
    )
    return ConversationHandler.END

async def admin_show_all_debts_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _check(update):
        return ConversationHandler.END
    debts = await get_all_debts(status_filter="active")
    if not debts:
        txt = "No active debts."
    else:
        txt = f"<b>Active Debts ({len(debts)})</b>\n\n"
        for d in debts[:15]:
            name = d.get("full_name", "")
            txt += f"• {name} (@{d['username']}) — Birr {d['amount']:.2f}\n"
    await update.message.reply_text(
        txt,
        reply_markup=await admin_debts_inline_keyboard("active"),
        parse_mode=ParseMode.HTML
    )
    return ConversationHandler.END

# --- Lock Menu ---

async def admin_lock_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _check(update):
        return ConversationHandler.END
    from keyboards import admin_lock_menu_inline_keyboard
    await update.message.reply_text(
        "Set daily stock limits for menu items:",
        reply_markup=await admin_lock_menu_inline_keyboard(),
        parse_mode=ParseMode.HTML
    )
    return ConversationHandler.END


# --- Payment Account Management ---

async def admin_payment_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _check(update):
        return ConversationHandler.END
    accounts = await get_payment_accounts()
    txt = "<b>Payment Accounts</b>\n\n"
    if accounts:
        for a in accounts:
            txt += f"• {a['bank_name']}: <code>{a['number']}</code> ({a['holder_name']})\n"
    else:
        txt += "No accounts yet."
    await update.message.reply_text(
        txt,
        reply_markup=await admin_payment_accounts_keyboard(),
        parse_mode=ParseMode.HTML
    )
    return ConversationHandler.END

async def _handle_payment_inline(update: Update, context: ContextTypes.DEFAULT_TYPE, query, data):
    if data.startswith("apay_del_"):
        pid = int(data.split("_")[2])
        await delete_payment_account(pid)
        await query.edit_message_text(
            "Deleted.",
            reply_markup=await admin_payment_accounts_keyboard(),
            parse_mode=ParseMode.HTML
        )
        return

    if data == "apay_add":
        context.user_data["expect_payment_bank"] = True
        await query.edit_message_text(
            "Enter the <b>bank name</b> (e.g. CBE, Abyssinia, Telebirr):",
            parse_mode=ParseMode.HTML
        )
        return

    if data == "apay_back":
        await query.edit_message_text(
            "<b>Admin Portal</b>",
            reply_markup=get_admin_keyboard(),
            parse_mode=ParseMode.HTML
        )

async def _finish_delivery(context, query, order_group, on_debt=False):
    await update_order_status(order_group, "Delivered")
    groups = await get_grouped_orders_by_status("Delivered")
    target = next((g for g in groups if g["order_group"] == order_group), None)
    if target:
        try:
            text = "<b>Order Delivered!</b>\n\nThank you for your order!"
            if on_debt:
                from database import add_debt as db_add_debt, get_user
                user = await get_user(target["user_id"])
                username = (user or {}).get("username") or "unknown"
                menu = await get_menu()
                items = target.get("items", [])
                total = sum(it["qty"] * menu.get(it["item"], 0) for it in items)
                full_name = (user or {}).get("full_name", username)
                await db_add_debt(
                    username=username,
                    full_name=full_name,
                    amount=total,
                    description=f"Delivered order #{order_group}",
                    order_group=order_group,
                    user_id=target["user_id"]
                )
                text += " <i>(recorded as debt)</i>"
            else:
                text += " 💰"
            await context.bot.send_message(
                target["user_id"],
                text,
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            pass
    original_text = query.message.text_html or query.message.text
    label = "✅ <b>DELIVERED (DEBT)</b>" if on_debt else "✅ <b>DELIVERED (PAID)</b>"
    await query.edit_message_text(
        original_text + "\n\n" + label,
        parse_mode=ParseMode.HTML
    )

# --- Debt inline callbacks ---

async def _handle_debt_inline(update: Update, context: ContextTypes.DEFAULT_TYPE, query, data):
    if data.startswith("adel_allow_"):
        username = data.replace("adel_allow_", "")
        await remove_from_debt_allow_list(username)
        await query.edit_message_text(
            f"Removed @{username} from allow list.",
            reply_markup=await admin_allow_list_inline_keyboard(),
            parse_mode=ParseMode.HTML
        )
        return

    if data == "admin_add_allow":
        context.user_data["expect_allow_username"] = True
        await query.edit_message_text(
            "Enter the Telegram <b>username</b> to allow for debt:",
            parse_mode=ParseMode.HTML
        )
        return

    if data == "admin_back_debt":
        await query.edit_message_text(
            "<b>Debt Management</b>",
            reply_markup=get_admin_debt_keyboard(),
            parse_mode=ParseMode.HTML
        )
        return

    if data.startswith("adebt_"):
        debt_id = int(data.split("_")[1])
        if data.startswith("adebt_paid_"):
            await mark_debt_paid(debt_id)
            await query.edit_message_text("Debt marked as paid ✅")
            return
        if data.startswith("adebt_waive_"):
            await waive_debt(debt_id)
            await query.edit_message_text("Debt waived 🚫")
            return
        # View debt detail
        from database import get_all_debts
        all_debts = await get_all_debts()
        debt = next((d for d in all_debts if d["id"] == debt_id), None)
        if debt:
            await query.edit_message_text(
                f"<b>Debt Detail</b>\n\n"
                f"User: {debt.get('full_name', '')} (@{debt['username']})\n"
                f"Amount: Birr {debt['amount']:.2f}\n"
                f"Status: {debt['status'].title()}\n"
                f"Description: {debt.get('description', '-')}\n"
                f"Created: {debt['created_at']}",
                reply_markup=admin_debt_action_keyboard(debt_id),
                parse_mode=ParseMode.HTML
            )
        return

    if data == "adebt_filter_active":
        debts = await get_all_debts(status_filter="active")
        txt = f"<b>Active Debts ({len(debts)})</b>\n\n"
        for d in debts[:15]:
            name = d.get("full_name", "")
            txt += f"• {name} (@{d['username']}) — Birr {d['amount']:.2f}\n"
        await query.edit_message_text(
            txt, reply_markup=await admin_debts_inline_keyboard("active"),
            parse_mode=ParseMode.HTML
        )
        return

    if data == "adebt_filter_all":
        debts = await get_all_debts()
        txt = f"<b>All Debts ({len(debts)})</b>\n\n"
        for d in debts[:15]:
            name = d.get("full_name", "")
            txt += f"• {name} (@{d['username']}) — Birr {d['amount']:.2f} ({d['status']})\n"
        await query.edit_message_text(
            txt, reply_markup=await admin_debts_inline_keyboard(),
            parse_mode=ParseMode.HTML
        )
        return

    if data == "adebt_back_to_list":
        debts = await get_all_debts(status_filter="active")
        txt = f"<b>Active Debts ({len(debts)})</b>\n\n"
        for d in debts[:15]:
            name = d.get("full_name", "")
            txt += f"• {name} (@{d['username']}) — Birr {d['amount']:.2f}\n"
        await query.edit_message_text(
            txt, reply_markup=await admin_debts_inline_keyboard("active"),
            parse_mode=ParseMode.HTML
        )
        return

# --- Inline Callback Handler ---

async def admin_inline_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not _check(update):
        return ConversationHandler.END

    data = query.data

    # --- Debt callbacks ---
    if data.startswith("adel_allow_") or data.startswith("adebt_") or data == "admin_add_allow" or data == "admin_back_debt" or data == "adebt_back_to_list" or data == "adebt_filter_active" or data == "adebt_filter_all":
        return await _handle_debt_inline(update, context, query, data)

    # --- Payment callbacks ---
    if data.startswith("apay_"):
        return await _handle_payment_inline(update, context, query, data)

    # --- Order management callbacks ---

    if data.startswith("ord_accept_") or data.startswith("ord_decline_"):
        parts = data.split("_", 2)
        action = parts[1]
        order_group = parts[2]
        menu = await get_menu()
        original_text = query.message.text_html or query.message.text

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
                        + f"\n\nTotal: Birr {total:.2f}\n\nYour order is being prepared."
                    )
                    await context.bot.send_message(target["user_id"], text, parse_mode=ParseMode.HTML)
                except:
                    pass
            await query.edit_message_text(
                original_text + "\n\n✅ <b>ACCEPTED</b>",
                reply_markup=order_ready_keyboard(order_group),
                parse_mode=ParseMode.HTML
            )
        else:
            context.user_data["decline_order_group"] = order_group
            context.user_data["decline_original_text"] = original_text
            context.user_data["decline_msg_chat_id"] = query.message.chat_id
            context.user_data["decline_msg_id"] = query.message.message_id
            context.user_data["decline_user_id"] = None
            groups = await get_grouped_orders_by_status("Pending")
            target = next((g for g in groups if g["order_group"] == order_group), None)
            if target:
                context.user_data["decline_user_id"] = target["user_id"]
            await query.edit_message_text(
                original_text + "\n\n⏳ <b>Waiting for decline reason...</b>",
                parse_mode=ParseMode.HTML
            )
            await context.bot.send_message(
                update.effective_user.id,
                "Type the reason for declining this order:",
                parse_mode=ParseMode.HTML
            )
            context.user_data["expect_decline_reason"] = True
        return ConversationHandler.END

    if data.startswith("noitem_"):
        order_group = data.split("_", 1)[1]
        from database import get_order_items
        items = await get_order_items(order_group)
        user_id = items[0].get("user_id") if items else None
        if not user_id:
            await query.edit_message_text("Could not find user for this order.")
            return ConversationHandler.END
        context.user_data["noitem_order_group"] = order_group
        context.user_data["noitem_user_id"] = user_id
        context.user_data["noitem_original_text"] = query.message.text_html or query.message.text
        context.user_data["noitem_msg_chat_id"] = query.message.chat_id
        context.user_data["noitem_msg_id"] = query.message.message_id
        await query.edit_message_text(
            context.user_data["noitem_original_text"] + "\n\n⏳ <b>Waiting for your message to the user...</b>",
            parse_mode=ParseMode.HTML
        )
        await context.bot.send_message(
            update.effective_user.id,
            "Type the message to send to the user about the missing item (money will be returned):",
            parse_mode=ParseMode.HTML
        )
        context.user_data["expect_noitem_msg"] = True
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
        original_text = query.message.text_html or query.message.text
        await query.edit_message_text(
            original_text + "\n\n🟡 <b>READY FOR PICKUP</b>",
            reply_markup=order_deliver_keyboard(order_group),
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END

    if data.startswith("ord_deliver_"):
        order_group = data.split("_", 2)[2]
        original_text = query.message.text_html or query.message.text
        await query.edit_message_text(
            original_text + "\n\n<b>Mark as?</b>",
            reply_markup=deliver_paid_debt_keyboard(order_group),
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END

    if data.startswith("ord_paid_"):
        order_group = data.split("_", 2)[2]
        await _finish_delivery(context, query, order_group, on_debt=False)
        return ConversationHandler.END

    if data.startswith("ord_debt_"):
        order_group = data.split("_", 2)[2]
        await _finish_delivery(context, query, order_group, on_debt=True)
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

    if data == "admin_add_category":
        await query.edit_message_text("Enter the <b>name</b> of the new category:", parse_mode=ParseMode.HTML)
        return ADMIN_ADD_CATEGORY

    if data.startswith("manage_cat_"):
        category = data.replace("manage_cat_", "")
        context.user_data["manage_category"] = category
        from keyboards import admin_category_keyboard
        items = await get_sub_menu(category)
        if items:
            lines = "\n".join(f"{n} - Birr {p}" for n, p in items.items())
            txt = f"<b>{category}</b> sub-items:\n\n{lines}"
        else:
            txt = f"<b>{category}</b> has no sub-items yet."
        await query.edit_message_text(txt, reply_markup=await admin_category_keyboard(category))
        return ConversationHandler.END

    if data.startswith("add_subitem_"):
        category = data.replace("add_subitem_", "")
        context.user_data["admin_sub_parent"] = category
        await query.edit_message_text(
            f"Enter the <b>name</b> of the sub-item under {category}:",
            parse_mode=ParseMode.HTML
        )
        return ADMIN_ADD_SUBITEM_NAME

    if data == "admin_back_menu":
        menu_items = await get_all_menu_items()
        txt = "<b>Menu</b>\n\n"
        cats = [r for r in menu_items if r["parent"] is None]
        for r in cats:
            sub = [s for s in menu_items if s["parent"] == r["name"]]
            if sub:
                txt += f"📁 <b>{r['name']}</b>\n"
                for s in sub:
                    txt += f"   {s['name']} - Birr {s['price']}\n"
            else:
                txt += f"{r['name']} - Birr {r['price']}\n"
        await query.edit_message_text(txt.strip(), reply_markup=await admin_menu_edit_keyboard())
        return ConversationHandler.END

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

    # --- Lock Menu callbacks ---

    if data == "lock_back" or data == "lock_back_list":
        from keyboards import get_admin_keyboard
        await query.edit_message_text("Cancelled.")
        return ConversationHandler.END

    if data == "lock_unlock_all":
        from database import get_all_menu_items, get_all_daily_stocks, clear_daily_stock
        today_stocks = await get_all_daily_stocks()
        for s in today_stocks:
            await clear_daily_stock(s["name"])
        items = await get_all_menu_items()
        await query.edit_message_text(
            "🔓 All limits cleared and unlocked.",
            reply_markup=await admin_lock_menu_inline_keyboard()
        )
        return ConversationHandler.END

    if data.startswith("locksel_"):
        name = data.replace("locksel_", "")
        from database import get_daily_stock
        stock = await get_daily_stock(name)
        if stock:
            locked = stock.get("locked", False)
            remaining = stock.get("remaining", 0)
            status = f"🔒 Locked" if locked else f"✅ {remaining}/{stock['max_qty']} remaining"
        else:
            status = "♾️ No limit set"
        await query.edit_message_text(
            f"<b>{name}</b>\n\nStatus: {status}\n\nEnter the <b>maximum quantity</b> for today (0 to disable):",
            reply_markup=await admin_lock_item_keyboard(name, stock),
            parse_mode=ParseMode.HTML
        )
        context.user_data["lock_menu_item"] = name
        context.user_data["expect_lock_qty"] = True
        return ConversationHandler.END

    if data.startswith("lock_toggle_"):
        name = data.replace("lock_toggle_", "")
        from database import get_daily_stock, toggle_lock_daily_stock
        stock = await get_daily_stock(name)
        new_locked = not stock.get("locked", False) if stock else True
        await toggle_lock_daily_stock(name, new_locked)
        stock = await get_daily_stock(name)
        await query.edit_message_text(
            f"<b>{name}</b>\n\nStatus: {'🔒 Locked' if new_locked else '🔓 Unlocked'}",
            reply_markup=await admin_lock_item_keyboard(name, stock),
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END

    if data.startswith("lock_clear_"):
        name = data.replace("lock_clear_", "")
        from database import clear_daily_stock
        await clear_daily_stock(name)
        await query.edit_message_text(
            f"❌ Limit cleared for <b>{name}</b>",
            reply_markup=await admin_lock_menu_inline_keyboard(),
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END

    return ConversationHandler.END
