from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler

from config import PAYMENT_CHOICE, PAYMENT_CONFIRM, COMMENT_CHOICE
from database import (
    get_payment_accounts, add_payment_account, delete_payment_account,
    save_order
)
from keyboards import (
    payment_methods_inline_keyboard, comment_choice_keyboard
)


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
            "After sending, paste the <b>confirmation message</b> you received from the bank or Telebirr below.\n\n"
            "⚠️ Do not send screenshots — paste the text message only.",
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

    bank = account.get("bank_name", "?")
    num = account.get("number", "?")
    holder = account.get("holder_name", "?")
    context.user_data["payment_info"] = f"{bank} - {num} ({holder})\nConfirmation: {confirmation}"
    context.user_data["on_debt"] = False

    await update.message.reply_text(
        f"Payment submitted! (Birr {context.user_data['order_total']:.2f})\n\nAny special instructions?",
        reply_markup=comment_choice_keyboard(),
        parse_mode=ParseMode.HTML
    )
    return COMMENT_CHOICE
