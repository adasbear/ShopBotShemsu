from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler

from config import HELP_MENU, ADMIN_USERNAMES
from utils.helpers import check_banned

HELP_TEXTS = {
    "order": (
        "<b>How to Order</b>\n\n"
        "1. Tap <b>Menu</b> from the main menu\n"
        "2. Select the items you want\n"
        "3. Enter the quantity\n"
        "4. Review your order and confirm\n"
        "5. Add special instructions if needed\n\n"
        "Your order will be sent to the admin for processing."
    ),
    "not_responding": (
        "<b>Bot Not Responding</b>\n\n"
        "If the bot is not responding:\n\n"
        "• Tap <b>Refresh</b> to reset your session\n"
        "• Check your internet connection\n"
        "• The bot may be under maintenance\n\n"
        "If the issue persists, use <b>Contact Admin</b> from the registration screen."
    ),
    "custom": (
        "<b>Custom Requests</b>\n\n"
        "Want something not on the menu?\n\n"
        "1. Tap <b>Menu</b>\n"
        "2. Tap <b>Other ✏️</b>\n"
        "3. Type what you want\n"
        "4. Enter the quantity\n\n"
        "The admin will receive your custom request."
    ),
    "edit_cancel": (
        "<b>Edit or Cancel Orders</b>\n\n"
        "You can edit or cancel <b>Pending</b> orders before 6PM:\n\n"
        "1. Tap <b>My Orders</b>\n"
        "2. Tap the order you want to modify\n"
        "3. Choose <b>Edit Items</b> or <b>Cancel Order</b>\n\n"
        "After 6PM, orders cannot be modified."
    ),
    "contact": (
        "<b>Contact Admin</b>\n\n"
        f"If you need help, send a message to @{ADMIN_USERNAMES[0]}:\n\n"
        "• Type <b>/start</b> and tap <b>Contact Admin</b>\n"
        f"• Or message @{ADMIN_USERNAMES[0]} directly on Telegram\n\n"
        "The admin will respond as soon as possible."
    ),
}

async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_banned(update, context):
        return ConversationHandler.END
    await update.message.reply_text(
        "<b>Help</b>\n\nSelect a topic below:",
        reply_markup=_help_keyboard(),
        parse_mode=ParseMode.HTML
    )
    return HELP_MENU

def _help_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("How to Order", callback_data="help_order")],
        [InlineKeyboardButton("Bot Not Responding", callback_data="help_not_responding")],
        [InlineKeyboardButton("Custom Requests", callback_data="help_custom")],
        [InlineKeyboardButton("Edit / Cancel Orders", callback_data="help_edit_cancel")],
        [InlineKeyboardButton("Contact Admin", callback_data="help_contact")],
    ])

async def handle_help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    topic = query.data.replace("help_", "")
    if topic == "back":
        await query.edit_message_text(
            "<b>Help</b>\n\nSelect a topic below:",
            reply_markup=_help_keyboard(),
            parse_mode=ParseMode.HTML
        )
    else:
        text = HELP_TEXTS.get(topic)
        if not text:
            await query.edit_message_text("Topic not found.")
            return HELP_MENU
        kb = [[InlineKeyboardButton("⬅ Back", callback_data="help_back")]]
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode=ParseMode.HTML
        )
    return HELP_MENU
