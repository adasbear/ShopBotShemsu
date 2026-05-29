from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler

from config import GIVING_FEEDBACK
from database import get_user_orders, save_feedback
from keyboards import get_main_keyboard
from utils.helpers import is_admin, check_banned

async def view_my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_banned(update, context):
        return ConversationHandler.END
    user_id = update.effective_user.id
    orders = await get_user_orders(user_id)
    if not orders:
        await update.message.reply_text("No orders yet.")
        return

    msg = "RECENT ORDERS\n\n"
    for item, qty, status in orders:
        msg += f"{item} (x{qty}) - {status}\n"
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

async def start_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_banned(update, context):
        return ConversationHandler.END
    if is_admin(update.effective_user.username):
        from handlers.admin import admin_show_feedback
        return await admin_show_feedback(update, context)
    await update.message.reply_text("Type your feedback:")
    return GIVING_FEEDBACK

async def save_feedback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    msg = update.message.text
    await save_feedback(user_id, msg)
    await update.message.reply_text(
        "Thanks for your feedback!",
        reply_markup=get_main_keyboard()
    )
    return ConversationHandler.END
