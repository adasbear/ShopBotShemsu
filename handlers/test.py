import random
import time
import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler

import database
from keyboards import get_test_keyboard, get_admin_keyboard


async def show_test_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "<b>Test Mode</b>\n\nChoose a test action:",
        reply_markup=get_test_keyboard(),
        parse_mode=ParseMode.HTML
    )
    return ConversationHandler.END


async def handle_test_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or "admin"

    try:
        items = await database.get_all_menu_items()
        orderable = [i for i in items if i.get("price", 0) > 0]
        if not orderable:
            await update.message.reply_text("No orderable menu items found.")
            return ConversationHandler.END

        pick = random.choice(orderable)
        name = pick["name"]
        price = pick.get("price", 0)
        qty = 1

        order_group = f"TEST-{user_id}-{int(time.time()*1000)}"
        await database.save_order(user_id, name, qty, order_group, "Pending")

        admin_ids = await database.get_admin_user_id()
        admin_text = (
            f"<b>🧪 TEST ORDER</b>\n\n"
            f"Placed by: @{username}\n"
            f"Item: {name} x{qty}\n"
            f"Price: Birr {price:.2f}\n"
            f"Order: {order_group}"
        )
        for aid in admin_ids:
            try:
                await context.bot.send_message(
                    chat_id=aid,
                    text=admin_text,
                    parse_mode=ParseMode.HTML
                )
            except Exception as e:
                logging.warning(f"Test order notify failed for admin {aid}: {e}")

        await update.message.reply_text(
            f"<b>✅ Test Order Placed</b>\n\n"
            f"Item: <b>{name}</b> x{qty}\n"
            f"Price: Birr {price:.2f}\n"
            f"Order Ref: <code>{order_group}</code>\n\n"
            f"Check <b>My Orders</b> or <b>Orders</b> to see it.",
            reply_markup=get_admin_keyboard(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logging.error(f"Test order failed: {e}", exc_info=True)
        await update.message.reply_text(f"Test order failed: {e}")

    return ConversationHandler.END
