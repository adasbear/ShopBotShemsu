from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler

from config import DEBT_CHOICE, COMMENT_CHOICE, PAYMENT_CHOICE
from database import (
    get_user, save_order, is_allowed_debt, add_debt,
    get_user_debts, get_user_active_debt_total, get_admin_user_id,
    get_payment_accounts, save_debt_payment
)
from keyboards import (
    debt_choice_keyboard, debt_not_allowed_keyboard,
    comment_choice_keyboard, get_main_keyboard,
    order_accept_decline_keyboard, payment_methods_inline_keyboard
)
from utils.helpers import check_banned


async def view_my_debt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_banned(update, context):
        return ConversationHandler.END
    username = update.effective_user.username
    if not username:
        await update.message.reply_text("You need a Telegram username to use this feature.")
        return ConversationHandler.END
    debts = await get_user_debts(username)
    active_total = await get_user_active_debt_total(username)
    if not debts:
        await update.message.reply_text(
            "<b>My Debt</b>\n\nNo debt records found.",
            reply_markup=get_main_keyboard(),
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END
    lines = [f"<b>Active Debt:</b> Birr {active_total:.2f}\n"]
    for d in debts:
        icon = {"active": "🕐", "paid": "✅", "waived": "🚫"}.get(d["status"], "❓")
        label = d.get("description", "Order")
        lines.append(
            f"{icon} Birr {d['amount']:.2f} — {label} "
            f"({d['status'].title()})"
        )
    kb = [[InlineKeyboardButton("Pay Now 💰", callback_data="debt_pay_start")]] if active_total > 0 else []
    await update.message.reply_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(kb) if kb else get_main_keyboard(),
        parse_mode=ParseMode.HTML
    )
    return ConversationHandler.END


async def handle_debt_pay_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "debt_pay_start":
        username = update.effective_user.username
        active_total = await get_user_active_debt_total(username)
        if active_total <= 0:
            await query.edit_message_text("No active debt to pay.")
            return
        context.user_data["debt_pay_amount"] = active_total
        context.user_data["debt_pay_username"] = username
        context.user_data["debt_pay_user_id"] = update.effective_user.id
        await query.edit_message_text(
            f"<b>Paying Debt:</b> Birr {active_total:.2f}\n\nSelect a payment method:",
            reply_markup=await payment_methods_inline_keyboard(prefix="debt_pay"),
            parse_mode=ParseMode.HTML
        )
        return

    if data == "debt_pay_back":
        await query.edit_message_text("Payment cancelled.")
        return

    if data.startswith("debt_pay_"):
        pid = int(data.split("_")[2])
        accounts = await get_payment_accounts()
        account = next((a for a in accounts if a["id"] == pid), None)
        if not account:
            await query.edit_message_text("Payment method not found.")
            return
        context.user_data["debt_pay_account"] = account
        context.user_data["expect_debt_pay_confirm"] = True
        await query.edit_message_text(
            f"<b>Transfer to:</b>\n\n"
            f"Bank: {account['bank_name']}\n"
            f"Account: <code>{account['number']}</code>\n"
            f"Name: {account['holder_name']}\n\n"
            "After sending, paste the <b>confirmation message</b> you received from the bank or Telebirr below.\n\n"
            "⚠️ Do not send screenshots — paste the text message only.",
            parse_mode=ParseMode.HTML
        )
        return


async def handle_debt_pay_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("expect_debt_pay_confirm"):
        return
    confirmation = update.message.text.strip()
    if not confirmation:
        await update.message.reply_text("Please paste the confirmation message.")
        return

    username = context.user_data.get("debt_pay_username")
    user_id = context.user_data.get("debt_pay_user_id")
    amount = context.user_data.get("debt_pay_amount")
    account = context.user_data.get("debt_pay_account", {})

    bank = account.get("bank_name", "?")
    num = account.get("number", "?")
    holder = account.get("holder_name", "?")
    pay_str = f"{bank} - {num} ({holder})\nConfirmation: {confirmation}"

    await save_debt_payment(username, user_id, amount, pay_str)

    context.user_data["expect_debt_pay_confirm"] = False
    for k in ["debt_pay_username", "debt_pay_user_id", "debt_pay_amount", "debt_pay_account"]:
        context.user_data.pop(k, None)

    await update.message.reply_text(
        f"Debt payment of Birr {amount:.2f} submitted! The admin will process it shortly.",
        parse_mode=ParseMode.HTML
    )

    admin_id = await get_admin_user_id()
    if admin_id:
        user_record = await get_user(user_id)
        full_name = (user_record or {}).get("full_name", username)
        await context.bot.send_message(
            chat_id=admin_id,
            text=(
                f"<b>DEBT PAYMENT FROM: {full_name} (@{username})</b>\n\n"
                f"Amount: Birr {amount:.2f}\n\n"
                f"Payment:\n{pay_str}"
            ),
            parse_mode=ParseMode.HTML
        )


async def handle_debt_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data

    if choice == "debt_cancel":
        await query.edit_message_text("Order Cancelled.")
        return ConversationHandler.END

    order_group = context.user_data.get("order_group")
    items = context.user_data.get("session_items", [])
    user_id = update.effective_user.id

    if choice == "pay_now":
        from handlers.payment import show_payment_methods
        return await show_payment_methods(update, context)

    if choice == "debt_take":
        username = update.effective_user.username
        if not username:
            await query.edit_message_text(
                "You need a Telegram username to take debt.",
                reply_markup=debt_not_allowed_keyboard()
            )
            return DEBT_CHOICE
        allowed = await is_allowed_debt(username)
        if allowed:
            from database import decrement_daily_stock
            for i in items:
                await decrement_daily_stock(i["item"])
                await save_order(user_id, i["item"], i["qty"], order_group)
            user_record = await get_user(user_id)
            full_name = (user_record or {}).get("full_name", username)
            await add_debt(
                username=username,
                full_name=full_name,
                amount=context.user_data["order_total"],
                description=f"Order #{order_group}",
                order_group=order_group,
                user_id=user_id
            )
            context.user_data["on_debt"] = True
            await query.edit_message_text(
                f"<b>Order placed on debt!</b>\n\n"
                f"Amount: Birr {context.user_data['order_total']:.2f}\n\n"
                "Any special instructions?",
                reply_markup=comment_choice_keyboard(),
                parse_mode=ParseMode.HTML
            )
            await _notify_admin_debt(context, username)
            return COMMENT_CHOICE
        await query.edit_message_text(
            "You are not eligible.\n\n"
            "Sorry, we retired from the charity business. Continued payment delays have forced us to suspend credit services.\n\n"
            "ዱቤ ለነገ  !!!!!",
            reply_markup=debt_not_allowed_keyboard(),
            parse_mode=ParseMode.HTML
        )
        return DEBT_CHOICE

    return DEBT_CHOICE


async def _notify_admin_debt(context, username):
    admin_ids = await get_admin_user_id()
    if not admin_ids:
        return
    from database import _db
    comment = context.user_data.get("order_comment")
    order_name = context.user_data.get("order_name", username)
    user_id = context.user_data.get("user_id")
    text = (
        f"<b>DEBT ORDER FROM: {order_name} (@{username})</b>\n\n"
        f"{chr(10).join(context.user_data['order_items'])}\n\n"
        f"TOTAL: Birr {context.user_data['order_total']:.2f}"
    )
    if comment:
        text += f"\n\n<b>Comment:</b> {comment}"
    if user_id:
        ref = await _db(lambda: _supabase.table("referrals")
            .select("referrer_id").eq("referred_id", user_id).limit(1).execute())
        if ref.data:
            referrer_id = ref.data[0]["referrer_id"]
            ref_user = await _db(lambda: _supabase.table("users")
                .select("username").eq("user_id", referrer_id).limit(1).execute())
            ref_username = ref_user.data[0]["username"] if ref_user.data else str(referrer_id)
            text += f"\n\n👤 <b>Referred by:</b> @{ref_username}"
    for admin_id in admin_ids:
        await context.bot.send_message(
            chat_id=admin_id,
            text=text,
            reply_markup=order_accept_decline_keyboard(context.user_data["order_group"]),
            parse_mode=ParseMode.HTML
        )
