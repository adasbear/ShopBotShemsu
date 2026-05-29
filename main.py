import os
import asyncio
import logging
import threading
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ConversationHandler

from config import BOT_TOKEN, REGISTRATION, MENU_SELECTION, QTY_INPUT, ADD_MORE_PROMPT, CONFIRM_ORDER, GIVING_FEEDBACK, ADMIN_BROADCAST, ADMIN_ADD_ITEM_NAME, ADMIN_ADD_ITEM_PRICE, CONTACT_ADMIN
from database import init_db

from handlers.start import start, register_user
from handlers.order import show_menu, handle_menu_selection, handle_qty, review_order, finalize_order
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

application = Application.builder().token(BOT_TOKEN).updater(None).connect_timeout(30).read_timeout(30).build()

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
    },
    fallbacks=[CommandHandler("start", start)],
)

application.add_handler(conv)
application.add_handler(CallbackQueryHandler(admin_inline_callback, pattern="^auser_|^aban_|^aunban_|^aback_users|^adel_|^admin_add_item|^deliver_|^ord_"))

_loop = None
_started = False

async def _init_app():
    global _started
    await application.initialize()
    await application.start()
    webhook_url = os.getenv("WEBHOOK_URL")
    if webhook_url:
        await application.bot.set_webhook(url=webhook_url)
        logging.info(f"Webhook set to {webhook_url}")
    _started = True

def _run_loop():
    global _loop
    _loop = asyncio.new_event_loop()
    asyncio.set_event_loop(_loop)
    _loop.run_until_complete(_init_app())
    _loop.run_forever()

threading.Thread(target=_run_loop, daemon=True).start()

@app.route("/webhook", methods=["POST"])
def webhook():
    if not _started:
        return "Initializing...", 503
    update = Update.de_json(request.get_json(force=True), application.bot)
    future = asyncio.run_coroutine_threadsafe(
        application.process_update(update), _loop
    )
    future.result(timeout=30)
    return "ok"

@app.route("/health")
def health():
    return "ok"

if __name__ == "__main__":
    app.run()
