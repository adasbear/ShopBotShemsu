import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler

from config import MENU_SELECTION, QTY_INPUT, ADD_MORE_PROMPT, CONFIRM_ORDER
from database import get_menu, save_order, get_user, get_admin_user_id
from keyboards import menu_inline_keyboard, add_more_or_review_keyboard, confirm_cancel_keyboard, order_accept_decline_keyboard
from utils.helpers import build_order_summary, check_banned

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_banned(update, context):
        return ConversationHandler.END
    context.user_data["session_items"] = []
    await update.message.reply_text(
        "SELECT ITEMS",
        reply_markup=await menu_inline_keyboard(),
        parse_mode=ParseMode.HTML
    )
    return MENU_SELECTION

async def handle_menu_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["current_item"] = query.data.replace("order_", "")
    await query.edit_message_text(
        f"How many <b>{context.user_data['current_item']}</b>?",
        parse_mode=ParseMode.HTML
    )
    return QTY_INPUT

async def handle_qty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    qty = update.message.text
    if not qty.isdigit():
        await update.message.reply_text("Enter a valid number.")
        return QTY_INPUT

    menu = await get_menu()
    item = context.user_data["current_item"]
    context.user_data["session_items"].append({
        "item": item, "qty": int(qty), "price": menu[item]
    })

    _, total = build_order_summary(context.user_data["session_items"])
    await update.message.reply_text(
        f"Added {qty}x {item}.",
        reply_markup=add_more_or_review_keyboard(total)
    )
    return ADD_MORE_PROMPT

async def review_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "add_more":
        menu = await get_menu()
        kb = [[InlineKeyboardButton(f"{k}", callback_data=f"order_{k}")] for k in menu]
        await query.edit_message_text(
            "Select another item:",
            reply_markup=InlineKeyboardMarkup(kb)
        )
        return MENU_SELECTION

    summary, total = build_order_summary(context.user_data["session_items"])
    text = f"FINAL ORDER REVIEW\n\n{summary}\n\nTOTAL: ${total:.2f}\n\nConfirm order?"

    await query.edit_message_text(
        text,
        reply_markup=confirm_cancel_keyboard(),
        parse_mode=ParseMode.HTML
    )
    return CONFIRM_ORDER

async def finalize_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "cancel":
        await query.edit_message_text("Order Cancelled.")
        return ConversationHandler.END

    user_id = update.effective_user.id
    user = await get_user(user_id)
    user_name = user["full_name"] if user else "Unknown"

    order_group = f"{user_id}_{int(time.time()*1000)}"
    items = context.user_data.get("session_items", [])
    total_cost = 0
    item_lines = []

    for i in items:
        cost = i["qty"] * i["price"]
        total_cost += cost
        item_lines.append(f"{i['qty']}x {i['item']} (${cost:.2f})")
        await save_order(user_id, i["item"], i["qty"], order_group)

    await query.edit_message_text(
        f"Order Placed!\nTotal: ${total_cost:.2f}",
        parse_mode=ParseMode.HTML
    )

    admin_id = await get_admin_user_id()
    if admin_id:
        admin_text = (
            f"<b>NEW ORDER FROM: {user_name}</b>\n\n"
            f"{chr(10).join(item_lines)}\n\n"
            f"TOTAL: ${total_cost:.2f}"
        )
        await context.bot.send_message(
            chat_id=admin_id,
            text=admin_text,
            reply_markup=order_accept_decline_keyboard(order_group),
            parse_mode=ParseMode.HTML
        )
    return ConversationHandler.END
