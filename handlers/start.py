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
    args = context.args or []

    if await check_banned(update, context):
        return ConversationHandler.END

    user = await get_user(user_id)

    if is_admin(username):
        from handlers.admin import show_admin_portal
        await show_admin_portal(update, context)
        return ConversationHandler.END

    if not user:
        for arg in args:
            if arg.startswith("ref_") and arg in ("ref_5407307505", "ref_7598009952"):
                ref_id = int(arg.replace("ref_", ""))
                context.user_data["referrer_id"] = ref_id
        welcome = (
            "<b>Welcome to Shemsu Shop! 🛒</b>\n\n"
            "Order your favourite food & drinks directly from this bot.\n\n"
            "• Browse the <b>Menu</b> and add items to your order\n"
            "• Track your <b>My Orders</b>\n"
            "• Add special instructions after ordering\n\n"
            "To get started, please enter your <b>Full Name</b> below:"
        )
        await update.message.reply_text(welcome, parse_mode=ParseMode.HTML)
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

    referrer_id = context.user_data.pop("referrer_id", None)
    if referrer_id and referrer_id in (5407307505, 7598009952):
        from database import create_referral
        await create_referral(referrer_id, user_id)
        try:
            await context.bot.send_message(
                referrer_id,
                f"🎉 <b>New Referral!</b>\n\n{full_name} just signed up using your referral link!",
                parse_mode=ParseMode.HTML
            )
        except:
            pass

    await update.message.reply_text(
        "Registered!",
        reply_markup=get_main_keyboard()
    )
    return ConversationHandler.END
