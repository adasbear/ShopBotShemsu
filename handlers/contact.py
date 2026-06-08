from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from config import CONTACT_ADMIN
from database import get_admin_user_id, get_user
from keyboards import get_banned_keyboard

async def contact_admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = await get_user(user_id)
    if not user or not user.get("banned"):
        await update.message.reply_text("You are not banned. No need to contact admin.")
        return ConversationHandler.END
    await update.message.reply_text(
        "Type your message to the admin:"
    )
    return CONTACT_ADMIN

async def contact_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    user = await get_user(user_id)
    if not user or not user.get("banned"):
        await query.edit_message_text("You are not banned.")
        return ConversationHandler.END
    await query.edit_message_text("Type your message to the admin:")
    return CONTACT_ADMIN

async def contact_admin_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = await get_user(user_id)
    name = user["full_name"] if user else "Unknown"
    msg = update.message.text
    username = update.effective_user.username or "no username"

    admin_ids = await get_admin_user_id()
    if admin_ids:
        for admin_id in admin_ids:
            try:
                await context.bot.send_message(
                    admin_id,
                    f"<b>Message from banned user</b>\n\n"
                    f"Name: {name}\n"
                    f"Username: @{username}\n"
                    f"User ID: {user_id}\n\n"
                    f"{msg}",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("Unban User", callback_data=f"aunban_{user_id}")
                    ]])
                )
            except:
                pass

    await update.message.reply_text(
        "Your message has been sent to the admin. They will review your case.",
        reply_markup=get_banned_keyboard()
    )
    return ConversationHandler.END
