import asyncio
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ConversationHandler

from config import BOT_TOKEN, REGISTRATION, MENU_SELECTION, QTY_INPUT, ADD_MORE_PROMPT, CONFIRM_ORDER, GIVING_FEEDBACK, ADMIN_BROADCAST, ADMIN_ADD_ITEM_NAME, ADMIN_ADD_ITEM_PRICE
from database import init_db

from handlers.start import start, register_user
from handlers.order import show_menu, handle_menu_selection, handle_qty, review_order, finalize_order
from handlers.admin import (
    show_admin_portal, admin_show_users, admin_show_menu,
    admin_show_orders, admin_show_summary, admin_show_individual,
    admin_mark_all, admin_start_broadcast,
    admin_do_broadcast, admin_add_item_start, admin_add_item_name,
    admin_add_item_price, admin_back_to_portal, admin_inline_callback
)
from handlers.feedback import view_my_orders, start_feedback, save_feedback_handler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

async def main():
    init_db()

    app = Application.builder().token(BOT_TOKEN).connect_timeout(30).read_timeout(30).build()

    conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("admin", show_admin_portal),
            MessageHandler(filters.Regex("^Menu$"), show_menu),
            MessageHandler(filters.Regex("^Feedback$"), start_feedback),
            MessageHandler(filters.Regex("^My Orders$"), view_my_orders),
            MessageHandler(filters.Regex("^Profile$"), start),
            # Admin entry points
            MessageHandler(filters.Regex("^Users$"), admin_show_users),
            MessageHandler(filters.Regex("^Manage Menu$"), admin_show_menu),
            MessageHandler(filters.Regex("^Orders$"), admin_show_orders),
            MessageHandler(filters.Regex("^Broadcast$"), admin_start_broadcast),
            MessageHandler(filters.Regex("^Summary$"), admin_show_summary),
            MessageHandler(filters.Regex("^Mark Delivered$"), admin_show_individual),
            MessageHandler(filters.Regex("^Mark All Arrived$"), admin_mark_all),
            MessageHandler(filters.Regex("^Back to Portal$"), admin_back_to_portal),
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
        },
        fallbacks=[CommandHandler("start", start)],
    )

    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(admin_inline_callback, pattern="^auser_|^aban_|^aunban_|^aback_users|^adel_|^admin_add_item|^deliver_"))

    async with app:
        await app.start()
        await app.updater.start_polling()
        logging.info("Bot is running...")
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            logging.info("Shutting down...")
        finally:
            await app.updater.stop()
            await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
