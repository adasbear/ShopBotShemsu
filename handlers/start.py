from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler

from config import REGISTRATION
from database import get_user, register_user as db_register_user
from keyboards import get_main_keyboard
from utils.helpers import is_admin, check_banned

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username

    if await check_banned(update, context):
        return ConversationHandler.END

    user = await get_user(user_id)

    if is_admin(username):
        from handlers.admin import show_admin_portal
        await show_admin_portal(update, context)
        return ConversationHandler.END

    if not user:
        await update.message.reply_text(
            "Welcome! Please enter your <b>Full Name</b> to register:",
            parse_mode=ParseMode.HTML
        )
        return REGISTRATION

    await update.message.reply_text(
        f"Welcome back, <b>{user['full_name']}</b>!",
        reply_markup=get_main_keyboard(),
        parse_mode=ParseMode.HTML
    )
    return ConversationHandler.END

async def register_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    full_name = update.message.text
    await db_register_user(user_id, full_name, update.effective_user.username)

    await update.message.reply_text(
        "Registered!",
        reply_markup=get_main_keyboard()
    )
    return ConversationHandler.END
