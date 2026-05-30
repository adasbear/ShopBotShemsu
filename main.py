import os
import asyncio
import logging
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ConversationHandler

from config import BOT_TOKEN, REGISTRATION, MENU_SELECTION, QTY_INPUT, ADD_MORE_PROMPT, CONFIRM_ORDER, GIVING_FEEDBACK, ADMIN_BROADCAST, ADMIN_ADD_ITEM_NAME, ADMIN_ADD_ITEM_PRICE, CONTACT_ADMIN, OTHER_ITEM_INPUT, COMMENT_CHOICE, ORDER_COMMENT
from database import init_db

from handlers.start import start, register_user
from handlers.order import show_menu, handle_menu_selection, handle_qty, review_order, finalize_order, handle_custom_item_name, handle_comment_choice, handle_order_comment
from handlers.admin import (
    show_admin_portal, admin_show_users, admin_show_menu,
    admin_show_orders, admin_show_new_orders, admin_show_accepted,
    admin_show_ready, admin_show_profit,
    admin_show_summary, admin_show_individual,
    admin_mark_all, admin_start_broadcast,
    admin_do_broadcast, admin_add_item_start, admin_add_item_name,
    admin_add_item_price, admin_back_to_portal, admin_inline_callback
)
from handlers.feedback import view_my_orders, start_feedback, save_feedback_handler
from handlers.contact import contact_admin_start, contact_admin_callback, contact_admin_send

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

app = Flask(__name__)

init_db()

application = Application.builder().token(BOT_TOKEN).connect_timeout(30).read_timeout(30).build()

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Cancelled.")
    return ConversationHandler.END

conv = ConversationHandler(
    entry_points=[
        CommandHandler("start", start),
        CommandHandler("admin", show_admin_portal),
        MessageHandler(filters.Regex("^Menu$"), show_menu),
        MessageHandler(filters.Regex("^Feedback$"), start_feedback),
        MessageHandler(filters.Regex("^My Orders$"), view_my_orders),
        MessageHandler(filters.Regex("^Profile$"), start),
        MessageHandler(filters.Regex("^Users$"), admin_show_users),
        MessageHandler(filters.Regex("^Manage Menu$"), admin_show_menu),
        MessageHandler(filters.Regex("^Orders$"), admin_show_orders),
        MessageHandler(filters.Regex("^New Orders$"), admin_show_new_orders),
        MessageHandler(filters.Regex("^Accepted$"), admin_show_accepted),
        MessageHandler(filters.Regex("^Ready$"), admin_show_ready),
        MessageHandler(filters.Regex("^Today's Profit$"), admin_show_profit),
        MessageHandler(filters.Regex("^Broadcast$"), admin_start_broadcast),
        MessageHandler(filters.Regex("^Summary$"), admin_show_summary),
        MessageHandler(filters.Regex("^Mark Delivered$"), admin_show_individual),
        MessageHandler(filters.Regex("^Mark All Arrived$"), admin_mark_all),
        MessageHandler(filters.Regex("^Back to Portal$"), admin_back_to_portal),
        MessageHandler(filters.Regex("^Contact Admin$"), contact_admin_start),
        CallbackQueryHandler(contact_admin_callback, pattern="^contact_admin$"),
    ],
    states={
        REGISTRATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_user)],
        MENU_SELECTION: [CallbackQueryHandler(handle_menu_selection)],
        QTY_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_qty)],
        ADD_MORE_PROMPT: [CallbackQueryHandler(review_order)],
        CONFIRM_ORDER: [CallbackQueryHandler(finalize_order)],
        GIVING_FEEDBACK: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_feedback_handler)],
        ADMIN_BROADCAST: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_do_broadcast)],
        ADMIN_ADD_ITEM_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_add_item_name)],
        ADMIN_ADD_ITEM_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_add_item_price)],
        CONTACT_ADMIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, contact_admin_send)],
        OTHER_ITEM_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_custom_item_name)],
        COMMENT_CHOICE: [CallbackQueryHandler(handle_comment_choice)],
        ORDER_COMMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_order_comment)],
    },
    fallbacks=[CommandHandler("start", start), CommandHandler("cancel", cancel)],
)

application.add_handler(conv)
application.add_handler(CallbackQueryHandler(admin_inline_callback, pattern="^auser_|^aban_|^aunban_|^aback_users|^adel_|^admin_add_item|^deliver_|^ord_"))

async def _start_polling():
    await application.bot.delete_webhook()
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    while True:
        await asyncio.sleep(3600)

def _run_bot():
    try:
        asyncio.run(_start_polling())
    except Exception as e:
        logging.error(f"Bot polling crashed: {e}")

threading.Thread(target=_run_bot, daemon=True).start()

@app.route("/")
def home():
    return "Bot is running."

@app.route("/health")
def health():
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
