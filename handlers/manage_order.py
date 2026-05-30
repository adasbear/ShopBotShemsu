from datetime import datetime, timezone

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler

from config import MANAGE_ORDER, ORDER_ACTION, EDIT_ITEM, EDIT_QTY
from database import get_user_grouped_orders, get_order_items, update_item_qty, cancel_order_group, get_admin_user_id
from keyboards import get_main_keyboard
from utils.helpers import check_banned


def _can_modify(timestamp_iso: str) -> bool:
    order_time = datetime.fromisoformat(timestamp_iso.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    if order_time.date() != now.date():
        return False
    return now.hour < 18


async def view_my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_banned(update, context):
        return ConversationHandler.END
    user_id = update.effective_user.id
    orders = await get_user_grouped_orders(user_id)
    if not orders:
        await update.message.reply_text("No orders yet.")
        return ConversationHandler.END

    kb = []
    for o in orders:
        icon = {"Pending": "🕐", "Delivered": "✅", "Cancelled": "❌"}.get(o["status"], "📦")
        ts = datetime.fromisoformat(o["timestamp"].replace("Z", "+00:00"))
        label = f"{icon} {ts.strftime('%b %d, %I:%M %p')} - {o['status']}"
        kb.append([InlineKeyboardButton(label, callback_data=f"myorder_{o['order_group']}")])

    await update.message.reply_text(
        "YOUR ORDERS\n\nTap an order to manage:",
        reply_markup=InlineKeyboardMarkup(kb)
    )
    return MANAGE_ORDER


async def handle_manage_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    order_group = query.data.replace("myorder_", "")
    context.user_data["manage_order_group"] = order_group

    items = await get_order_items(order_group)
    context.user_data["manage_items"] = items

    status = items[0]["status"] if items else "Unknown"
    timestamp = items[0]["timestamp"] if items else ""

    lines = [f"{i['qty']}x {i['item']}" for i in items]

    if status != "Pending" or not _can_modify(timestamp):
        await query.edit_message_text(
            f"<b>ORDER ({status})</b>\n\n" + "\n".join(lines) + "\n\nThis order cannot be modified.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅ Back", callback_data="back_to_orders")]]),
            parse_mode=ParseMode.HTML
        )
        return ORDER_ACTION

    kb = [
        [InlineKeyboardButton("Edit Items ✏️", callback_data="edit_order")],
        [InlineKeyboardButton("Cancel Order ❌", callback_data="cancel_order")],
        [InlineKeyboardButton("⬅ Back", callback_data="back_to_orders")]
    ]
    await query.edit_message_text(
        f"<b>ORDER (Pending)</b>\n\n" + "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode=ParseMode.HTML
    )
    return ORDER_ACTION


async def handle_order_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action = query.data

    if action == "back_to_orders":
        user_id = update.effective_user.id
        orders = await get_user_grouped_orders(user_id)
        if not orders:
            await query.edit_message_text("No orders yet.")
            return ConversationHandler.END
        kb = []
        for o in orders:
            icon = {"Pending": "🕐", "Delivered": "✅", "Cancelled": "❌"}.get(o["status"], "📦")
            ts = datetime.fromisoformat(o["timestamp"].replace("Z", "+00:00"))
            label = f"{icon} {ts.strftime('%b %d, %I:%M %p')} - {o['status']}"
            kb.append([InlineKeyboardButton(label, callback_data=f"myorder_{o['order_group']}")])
        await query.edit_message_text(
            "YOUR ORDERS\n\nTap an order to manage:",
            reply_markup=InlineKeyboardMarkup(kb)
        )
        return MANAGE_ORDER

    if action == "edit_order":
        items = context.user_data.get("manage_items", [])
        kb = []
        for i in items:
            kb.append([InlineKeyboardButton(f"{i['qty']}x {i['item']} ✏️", callback_data=f"edititem_{i['id']}")])
        kb.append([InlineKeyboardButton("✅ Done Editing", callback_data="done_editing")])
        await query.edit_message_text(
            "EDIT ITEMS\n\nTap an item to change its quantity:",
            reply_markup=InlineKeyboardMarkup(kb)
        )
        return EDIT_ITEM

    if action == "cancel_order":
        kb = [
            [InlineKeyboardButton("Yes, Cancel it ❌", callback_data="confirm_cancel")],
            [InlineKeyboardButton("⬅ No, Keep it", callback_data="back_to_order")]
        ]
        await query.edit_message_text(
            "Are you sure you want to cancel this order?",
            reply_markup=InlineKeyboardMarkup(kb)
        )
        return ORDER_ACTION

    if action == "confirm_cancel":
        order_group = context.user_data["manage_order_group"]
        await cancel_order_group(order_group)
        admin_id = await get_admin_user_id()
        if admin_id:
            user = update.effective_user
            name = user.full_name or user.username or str(user.id)
            await context.bot.send_message(
                chat_id=admin_id,
                text=f"<b>ORDER CANCELLED BY USER</b>\n\nUser: {name}",
                parse_mode=ParseMode.HTML
            )
        await query.edit_message_text("Order cancelled.")
        return ConversationHandler.END

    if action == "back_to_order":
        items = context.user_data.get("manage_items", [])
        lines = [f"{i['qty']}x {i['item']}" for i in items]
        kb = [
            [InlineKeyboardButton("Edit Items ✏️", callback_data="edit_order")],
            [InlineKeyboardButton("Cancel Order ❌", callback_data="cancel_order")],
            [InlineKeyboardButton("⬅ Back", callback_data="back_to_orders")]
        ]
        await query.edit_message_text(
            f"<b>ORDER (Pending)</b>\n\n" + "\n".join(lines),
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode=ParseMode.HTML
        )
        return ORDER_ACTION

    return ORDER_ACTION


async def handle_edit_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "done_editing":
        await query.edit_message_text("Order updated!", reply_markup=get_main_keyboard())
        return ConversationHandler.END

    item_id = int(query.data.replace("edititem_", ""))
    context.user_data["editing_item_id"] = item_id

    for i in context.user_data.get("manage_items", []):
        if i["id"] == item_id:
            await query.edit_message_text(
                f"New quantity for <b>{i['item']}</b> (current: {i['qty']}):",
                parse_mode=ParseMode.HTML
            )
            break

    return EDIT_QTY


async def handle_edit_qty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text.isdigit() or int(text) == 0:
        await update.message.reply_text("Enter a number greater than 0.")
        return EDIT_QTY

    new_qty = int(text)
    item_id = context.user_data["editing_item_id"]
    await update_item_qty(item_id, new_qty)

    order_group = context.user_data["manage_order_group"]
    items = await get_order_items(order_group)
    context.user_data["manage_items"] = items

    kb = []
    for i in items:
        kb.append([InlineKeyboardButton(f"{i['qty']}x {i['item']} ✏️", callback_data=f"edititem_{i['id']}")])
    kb.append([InlineKeyboardButton("✅ Done Editing", callback_data="done_editing")])
    await update.message.reply_text(
        "EDIT ITEMS\n\nTap an item to change its quantity:",
        reply_markup=InlineKeyboardMarkup(kb)
    )
    return EDIT_ITEM
