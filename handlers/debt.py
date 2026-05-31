from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler

from config import DEBT_CHOICE, COMMENT_CHOICE
from database import (
    get_user, save_order, is_allowed_debt, add_debt,
    get_user_debts, get_user_active_debt_total, get_admin_user_id
)
from keyboards import (
    debt_choice_keyboard, debt_not_allowed_keyboard,
    comment_choice_keyboard, get_main_keyboard,
    order_accept_decline_keyboard
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
        lines.append(
            f"{icon} Birr {d['amount']:.2f} — {d.get('description', 'Order')} "
            f"({d['status'].title()})"
        )
    await update.message.reply_text(
        "\n".join(lines),
        reply_markup=get_main_keyboard(),
        parse_mode=ParseMode.HTML
    )
    return ConversationHandler.END


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
        for i in items:
            await save_order(user_id, i["item"], i["qty"], order_group)
        await query.edit_message_text(
            f"Order Placed! (Birr {context.user_data['order_total']:.2f})\n\nAny special instructions?",
            reply_markup=comment_choice_keyboard(),
            parse_mode=ParseMode.HTML
        )
        return COMMENT_CHOICE

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
            for i in items:
                await save_order(user_id, i["item"], i["qty"], order_group)
            await add_debt(
                username=username,
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
            "You are <b>not approved</b> for debt.\n\n"
            "Ask the admin to add you to the allow list, or pay now.",
            reply_markup=debt_not_allowed_keyboard(),
            parse_mode=ParseMode.HTML
        )
        return DEBT_CHOICE

    return DEBT_CHOICE


async def _notify_admin_debt(context, username):
    admin_id = await get_admin_user_id()
    if not admin_id:
        return
    comment = context.user_data.get("order_comment")
    text = (
        f"<b>DEBT ORDER FROM: @{username}</b>\n\n"
        f"{chr(10).join(context.user_data['order_items'])}\n\n"
        f"TOTAL: Birr {context.user_data['order_total']:.2f}"
    )
    if comment:
        text += f"\n\n<b>Comment:</b> {comment}"
    await context.bot.send_message(
        chat_id=admin_id,
        text=text,
        reply_markup=order_accept_decline_keyboard(context.user_data["order_group"]),
        parse_mode=ParseMode.HTML
    )
