import os
import asyncio
import logging
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ConversationHandler

from config import BOT_TOKEN, REGISTRATION, MENU_SELECTION, QTY_INPUT, ADD_MORE_PROMPT, CONFIRM_ORDER, GIVING_FEEDBACK, ADMIN_BROADCAST, ADMIN_ADD_ITEM_NAME, ADMIN_ADD_ITEM_PRICE, CONTACT_ADMIN, OTHER_ITEM_INPUT, COMMENT_CHOICE, ORDER_COMMENT, MANAGE_ORDER, ORDER_ACTION, EDIT_ITEM, EDIT_QTY, ADMIN_ADD_CATEGORY, ADMIN_MANAGE_CATEGORY, ADMIN_ADD_SUBITEM_NAME, ADMIN_ADD_SUBITEM_PRICE, HELP_MENU, DEBT_CHOICE
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
    admin_add_item_price, admin_add_category_start, admin_add_category_name,
    admin_add_sub_item_start, admin_add_sub_item_name, admin_add_sub_item_price,
    admin_back_to_portal, admin_inline_callback,
    admin_debt_menu, admin_show_allow_list,
    admin_show_all_debts_handler
)
from handlers.manage_order import view_my_orders, handle_manage_order, handle_order_action, handle_edit_item, handle_edit_qty
from handlers.feedback import start_feedback, save_feedback_handler
from handlers.help import show_help, handle_help_callback
from handlers.debt import view_my_debt, handle_debt_choice
from handlers.contact import contact_admin_start, contact_admin_callback, contact_admin_send

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

app = Flask(__name__)

init_db()

async def _seed_debts():
    from database import seed_debts_from_json
    initial_debts = [
        {"name": "Eman", "telegram_username": "@e3maan", "debt_etb": 280.00},
        {"name": "Leul", "telegram_username": "@Leul_et", "debt_etb": 275.00},
        {"name": "Mulisa", "telegram_username": "@Ofargadhu", "debt_etb": 270.00},
        {"name": "Hawi", "telegram_username": "@Hawii_z", "debt_etb": 210.00},
        {"name": "Kidus", "telegram_username": "@Kidus_1221", "debt_etb": 170.00},
        {"name": "Elias", "telegram_username": "@Ten_Duotrigintillion_googol", "debt_etb": 140.00},
        {"name": "Aman AI", "telegram_username": "@Im_not_aman", "debt_etb": 130.00},
        {"name": "Murad", "telegram_username": "@Raadmu", "debt_etb": 130.00},
        {"name": "Saron", "telegram_username": "@SFTM123", "debt_etb": 130.00},
        {"name": "Heran", "telegram_username": "@moriah_12", "debt_etb": 120.00},
        {"name": "Gebre", "telegram_username": "@Userg7", "debt_etb": 80.00},
        {"name": "Bereket", "telegram_username": "@Bek_i79", "debt_etb": 80.00},
        {"name": "Ayaan", "telegram_username": "@Kage_loitts", "debt_etb": 80.00},
        {"name": "Firaol", "telegram_username": "@ra_pha7", "debt_etb": 80.00},
        {"name": "Hachalu", "telegram_username": "@HAC_TAR", "debt_etb": 70.00},
        {"name": "Chala", "telegram_username": "@CANase12", "debt_etb": 10.00},
        {"name": "Yonas", "telegram_username": "@Yonasasmare", "debt_etb": 340.00},
        {"name": "Kalid", "telegram_username": "@kalid1287", "debt_etb": 420.00},
        {"name": "Ebba", "telegram_username": "@sco_w", "debt_etb": 540.00},
        {"name": "Dagi", "telegram_username": "@DagmawiTeweldebrhan", "debt_etb": 540.00},
        {"name": "Ayzobel", "telegram_username": "@NathnaelAyizohibel", "debt_etb": 660.00},
        {"name": "Barok", "telegram_username": "@B_rey123", "debt_etb": 670.00},
        {"name": "Barkot", "telegram_username": "@Bbarke", "debt_etb": 680.00},
        {"name": "Oliyad", "telegram_username": "@LAZARUS_Lazer", "debt_etb": 710.00},
        {"name": "Sol", "telegram_username": "@astrosol7", "debt_etb": 720.00},
        {"name": "Hundaol", "telegram_username": "@sieresete", "debt_etb": 740.00},
        {"name": "Halid", "telegram_username": "@halid64", "debt_etb": 750.00},
        {"name": "Mahlet", "telegram_username": "@Mahiletal", "debt_etb": 780.00},
        {"name": "Emran", "telegram_username": "@i_mra_n1", "debt_etb": 1065.00},
        {"name": "Sifen", "telegram_username": "@Huhh_33", "debt_etb": 1080.00},
        {"name": "Nebiyu", "telegram_username": "@thethess", "debt_etb": 1150.00},
        {"name": "she", "telegram_username": "@Jo21fr", "debt_etb": 1340.00},
        {"name": "Bruno", "telegram_username": "@BcubeJW", "debt_etb": 2650.00},
        {"name": "Aman Tarik", "telegram_username": "@AMANUEL389", "debt_etb": 3125.00},
        {"name": "Nahom", "telegram_username": "@nahomdz", "debt_etb": 3505.00}
    ]
    count = await seed_debts_from_json(initial_debts)
    if count:
        logging.info(f"Seeded {count} initial debt records.")

try:
    asyncio.run(_seed_debts())
except Exception as e:
    logging.warning(f"Debt seeding skipped: {e}")

application = Application.builder().token(BOT_TOKEN).connect_timeout(30).read_timeout(30).build()

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Cancelled.")
    return ConversationHandler.END

conv = ConversationHandler(
    entry_points=[
        CommandHandler("start", start),
        CommandHandler("admin", show_admin_portal),
        MessageHandler(filters.Regex("^Help$"), show_help),
        MessageHandler(filters.Regex("^Refresh$"), start),
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
        MessageHandler(filters.Regex("^My Debt$"), view_my_debt),
        MessageHandler(filters.Regex("^Debt Management$"), admin_debt_menu),
        MessageHandler(filters.Regex("^Allow List$"), admin_show_allow_list),
        MessageHandler(filters.Regex("^All Debts$"), admin_show_all_debts_handler),
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
        ADMIN_ADD_CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_add_category_name)],
        ADMIN_ADD_SUBITEM_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_add_sub_item_name)],
        ADMIN_ADD_SUBITEM_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_add_sub_item_price)],
        CONTACT_ADMIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, contact_admin_send)],
        OTHER_ITEM_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_custom_item_name)],
        COMMENT_CHOICE: [CallbackQueryHandler(handle_comment_choice)],
        ORDER_COMMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_order_comment)],
        MANAGE_ORDER: [CallbackQueryHandler(handle_manage_order)],
        ORDER_ACTION: [CallbackQueryHandler(handle_order_action)],
        EDIT_ITEM: [CallbackQueryHandler(handle_edit_item)],
        EDIT_QTY: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_edit_qty)],
        HELP_MENU: [CallbackQueryHandler(handle_help_callback, pattern="^help_")],
        DEBT_CHOICE: [CallbackQueryHandler(handle_debt_choice)],
    },
    fallbacks=[CommandHandler("start", start), CommandHandler("cancel", cancel)],
)

application.add_handler(conv)

async def _handle_allow_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("expect_allow_username"):
        return
    from utils.helpers import is_admin
    if not is_admin(update.effective_user.username):
        context.user_data["expect_allow_username"] = False
        return
    username = update.message.text.strip().lstrip("@")
    if not username:
        await update.message.reply_text("Invalid username.")
        return
    from database import add_to_debt_allow_list
    await add_to_debt_allow_list(username, update.effective_user.id)
    context.user_data["expect_allow_username"] = False
    from keyboards import get_admin_debt_keyboard
    await update.message.reply_text(
        f"@{username} added to allow list!",
        reply_markup=get_admin_debt_keyboard()
    )

application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, _handle_allow_username))
application.add_handler(CallbackQueryHandler(admin_inline_callback, pattern="^auser_|^aban_|^aunban_|^aback_users|^adel_|^admin_add_item|^admin_add_category|^manage_cat_|^add_subitem_|^admin_back_menu|^deliver_|^ord_|^adel_allow_|^adebt_|^admin_add_allow|^admin_back_debt|^adebt_back_to_list|^adebt_filter_"))

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
