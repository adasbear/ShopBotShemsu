from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler

from config import PAYMENT_CHOICE, PAYMENT_CONFIRM, COMMENT_CHOICE
from database import (
    get_payment_accounts, add_payment_account, delete_payment_account,
    get_admin_user_id, save_order
)
from keyboards import (
    payment_methods_inline_keyboard, comment_choice_keyboard,
    get_main_keyboard, order_accept_decline_keyboard,
    get_admin_payment_keyboard
)
from utils.helpers import check_banned


async def show_payment_methods(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text(
        "Select a payment method:",
        reply_markup=await payment_methods_inline_keyboard(),
        parse_mode=ParseMode.HTML
    )
    return PAYMENT_CHOICE


async def handle_payment_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "pay_back":
        await query.edit_message_text("Order Cancelled.")
        return ConversationHandler.END

    if data.startswith("pay_"):
        pid = int(data.split("_")[1])
        accounts = await get_payment_accounts()
        account = next((a for a in accounts if a["id"] == pid), None)
        if not account:
            await query.edit_message_text("Payment method not found.")
            return ConversationHandler.END
        context.user_data["selected_payment"] = account
        await query.edit_message_text(
            f"<b>Transfer to:</b>\n\n"
            f"Bank: {account['bank_name']}\n"
            f"Account: <code>{account['number']}</code>\n"
            f"Name: {account['holder_name']}\n\n"
            "After sending, paste the <b>confirmation message</b> you received from the bank or Telebirr below:",
            parse_mode=ParseMode.HTML
        )
        return PAYMENT_CONFIRM

    return PAYMENT_CHOICE


async def handle_payment_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    confirmation = update.message.text.strip()
    if not confirmation:
        await update.message.reply_text("Please paste the confirmation message.")
        return PAYMENT_CONFIRM

    user_id = update.effective_user.id
    order_group = context.user_data.get("order_group")
    items = context.user_data.get("session_items", [])
    account = context.user_data.get("selected_payment", {})

    for i in items:
        await save_order(user_id, i["item"], i["qty"], order_group)

    context.user_data["payment_confirmation"] = confirmation
    context.user_data["on_debt"] = False

    await _notify_admin_payment(context, user_id, account, confirmation)

    await update.message.reply_text(
        f"Payment submitted! (Birr {context.user_data['order_total']:.2f})\n\nAny special instructions?",
        reply_markup=comment_choice_keyboard(),
        parse_mode=ParseMode.HTML
    )
    return COMMENT_CHOICE


async def _notify_admin_payment(context, user_id, account, confirmation):
    admin_id = await get_admin_user_id()
    if not admin_id:
        return
    name = context.user_data.get("order_name", "Unknown")
    text = (
        f"<b>PAID ORDER FROM: {name}</b>\n\n"
        f"{chr(10).join(context.user_data['order_items'])}\n\n"
        f"TOTAL: Birr {context.user_data['order_total']:.2f}\n\n"
        f"<b>Payment:</b>\n"
        f"Bank: {account['bank_name']}\n"
        f"Account: <code>{account['number']}</code>\n"
        f"Name: {account['holder_name']}\n"
        f"Confirmation: {confirmation}"
    )
    await context.bot.send_message(
        chat_id=admin_id,
        text=text,
        reply_markup=order_accept_decline_keyboard(context.user_data["order_group"]),
        parse_mode=ParseMode.HTML
    )
