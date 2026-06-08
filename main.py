import os
import asyncio
import logging
import random
import threading
import requests
from datetime import datetime, timezone, timedelta
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from telegram import Update, MenuButtonWebApp, WebAppInfo
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ConversationHandler

from config import BOT_TOKEN, ADMIN_USERNAMES, REGISTRATION, MENU_SELECTION, QTY_INPUT, ADD_MORE_PROMPT, CONFIRM_ORDER, GIVING_FEEDBACK, ADMIN_BROADCAST, ADMIN_ADD_ITEM_NAME, ADMIN_ADD_ITEM_PRICE, CONTACT_ADMIN, OTHER_ITEM_INPUT, COMMENT_CHOICE, ORDER_COMMENT, MANAGE_ORDER, ORDER_ACTION, EDIT_ITEM, EDIT_QTY, ADMIN_ADD_CATEGORY, ADMIN_MANAGE_CATEGORY, ADMIN_ADD_SUBITEM_NAME, ADMIN_ADD_SUBITEM_PRICE, HELP_MENU, DEBT_CHOICE, PAYMENT_CHOICE, PAYMENT_CONFIRM, PYRO_API_ID
import database
from database import init_db, _db, get_admin_user_id
from otp_sender import send_otp

from handlers.start import start, register_user
from handlers.order import show_menu, handle_menu_selection, handle_qty, review_order, finalize_order, handle_comment_choice, handle_order_comment
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
    admin_show_all_debts_handler, admin_payment_menu,
    admin_no_item_start, admin_lock_menu,
    admin_photo_start, admin_photo_handle_text, admin_photo_handle_photo,
    admin_photo_remove, admin_photo_handle_skip
)
from handlers.manage_order import view_my_orders, handle_manage_order, handle_order_action, handle_edit_item, handle_edit_qty
from handlers.feedback import start_feedback, save_feedback_handler
from handlers.help import show_help, handle_help_callback
from handlers.debt import view_my_debt, handle_debt_choice, handle_debt_pay_callback, handle_debt_pay_confirmation
from handlers.payment import handle_payment_choice, handle_payment_confirmation
from handlers.contact import contact_admin_start, contact_admin_callback, contact_admin_send
from handlers.test import show_test_menu, handle_test_order

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

app = Flask(__name__)
CORS(app)

init_db()

async def _seed_payment_accounts():
    from database import seed_payment_accounts
    count = await seed_payment_accounts()
    if count:
        logging.info(f"Seeded {count} default payment accounts.")

try:
    asyncio.run(_seed_payment_accounts())
except Exception as e:
    logging.warning(f"Payment seeding skipped: {e}")

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

WEBAPP_URL = "https://shopbotshemsu-1.onrender.com/app/"

async def webapp_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from telegram import WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("Open Shop 🛍️", web_app=WebAppInfo(url=WEBAPP_URL))
    ]])
    await update.message.reply_text("Tap to open the Shop Mini App:", reply_markup=kb)

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
        MessageHandler(filters.Regex("^No Item 📦$"), admin_no_item_start),
        MessageHandler(filters.Regex("^Lock Menu 🔒$"), admin_lock_menu),
        MessageHandler(filters.Regex("^Back to Portal$"), admin_back_to_portal),
        MessageHandler(filters.Regex("^My Debt$"), view_my_debt),
        MessageHandler(filters.Regex("^Payment Accounts$"), admin_payment_menu),
        MessageHandler(filters.Regex("^Manage Payments$"), admin_payment_menu),
        MessageHandler(filters.Regex("^Debt Management$"), admin_debt_menu),
        MessageHandler(filters.Regex("^Allow List$"), admin_show_allow_list),
        MessageHandler(filters.Regex("^All Debts$"), admin_show_all_debts_handler),
        MessageHandler(filters.Regex("^Contact Admin$"), contact_admin_start),
        CallbackQueryHandler(contact_admin_callback, pattern="^contact_admin$"),
        MessageHandler(filters.Regex("^Test$"), show_test_menu),
        MessageHandler(filters.Regex("^Test Order$"), handle_test_order),
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

        COMMENT_CHOICE: [CallbackQueryHandler(handle_comment_choice)],
        ORDER_COMMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_order_comment)],
        MANAGE_ORDER: [CallbackQueryHandler(handle_manage_order)],
        ORDER_ACTION: [CallbackQueryHandler(handle_order_action)],
        EDIT_ITEM: [CallbackQueryHandler(handle_edit_item)],
        EDIT_QTY: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_edit_qty)],
        HELP_MENU: [CallbackQueryHandler(handle_help_callback, pattern="^help_")],
        DEBT_CHOICE: [CallbackQueryHandler(handle_debt_choice)],
        PAYMENT_CHOICE: [CallbackQueryHandler(handle_payment_choice)],
        PAYMENT_CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_payment_confirmation)],
    },
    fallbacks=[CommandHandler("start", start), CommandHandler("cancel", cancel)],
)

application.add_handler(conv)
application.add_handler(CommandHandler("app", webapp_command))

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

async def _handle_payment_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get("expect_payment_input")
    if not step:
        return
    from utils.helpers import is_admin
    if not is_admin(update.effective_user.username):
        context.user_data["expect_payment_input"] = None
        return
    text = update.message.text.strip()
    if not text:
        await update.message.reply_text("Input cannot be empty.")
        return
    from database import add_payment_account
    from keyboards import get_admin_payment_keyboard, admin_payment_accounts_keyboard
    if step == "bank":
        context.user_data["payment_new_bank"] = text
        context.user_data["expect_payment_input"] = "number"
        await update.message.reply_text("Enter the <b>account number</b>:", parse_mode=ParseMode.HTML)
        return
    if step == "number":
        context.user_data["payment_new_number"] = text
        context.user_data["expect_payment_input"] = "holder"
        await update.message.reply_text("Enter the <b>account holder name</b>:", parse_mode=ParseMode.HTML)
        return
    if step == "holder":
        bank = context.user_data.pop("payment_new_bank", "Unknown")
        number = context.user_data.pop("payment_new_number", "Unknown")
        context.user_data["expect_payment_input"] = None
        await add_payment_account(bank, number, text)
        await update.message.reply_text(
            f"Added {bank} - {number} ({text})!",
            reply_markup=get_admin_payment_keyboard()
        )

async def _handle_decline_reason(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("expect_decline_reason"):
        return
    reason = update.message.text.strip()
    if not reason:
        await update.message.reply_text("Reason cannot be empty.")
        return
    from database import save_order_decline_reason, update_order_status
    order_group = context.user_data.get("decline_order_group")
    user_id = context.user_data.get("decline_user_id")
    original_text = context.user_data.get("decline_original_text", "")
    chat_id = context.user_data.get("decline_msg_chat_id")
    msg_id = context.user_data.get("decline_msg_id")
    await save_order_decline_reason(order_group, reason)
    await update_order_status(order_group, "Cancelled")
    if user_id:
        try:
            await context.bot.send_message(
                user_id,
                f"<b>Order Declined</b>\n\n<b>Reason:</b> {reason}\n\nContact @{ADMIN_USERNAMES[0]} if you have questions.",
                parse_mode=ParseMode.HTML
            )
        except:
            pass
    if chat_id and msg_id:
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg_id,
                text=original_text + f"\n\n❌ <b>DECLINED</b>\nReason: {reason}",
                parse_mode=ParseMode.HTML
            )
        except:
            pass
    context.user_data["expect_decline_reason"] = False
    for k in ["decline_order_group", "decline_user_id", "decline_original_text", "decline_msg_chat_id", "decline_msg_id"]:
        context.user_data.pop(k, None)
    await update.message.reply_text(
        f"Order declined with reason: {reason}",
        parse_mode=ParseMode.HTML
    )

async def _handle_noitem_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("expect_noitem_msg"):
        return
    msg = update.message.text.strip()
    if not msg:
        await update.message.reply_text("Message cannot be empty.")
        return
    from database import save_order_decline_reason, update_order_status
    order_group = context.user_data.get("noitem_order_group")
    user_id = context.user_data.get("noitem_user_id")
    original_text = context.user_data.get("noitem_original_text", "")
    chat_id = context.user_data.get("noitem_msg_chat_id")
    msg_id = context.user_data.get("noitem_msg_id")
    full_msg = f"{msg}\n\n⚠️ Your money will be returned shortly."
    await save_order_decline_reason(order_group, full_msg)
    await update_order_status(order_group, "Cancelled")
    if user_id:
        try:
            await context.bot.send_message(
                user_id,
                f"<b>Item Not Available</b>\n\n{full_msg}\n\nContact @{ADMIN_USERNAMES[0]} if you have questions.",
                parse_mode=ParseMode.HTML
            )
        except:
            pass
    if chat_id and msg_id:
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg_id,
                text=original_text + f"\n\n❌ <b>NO ITEM</b>\nMessage: {msg}",
                parse_mode=ParseMode.HTML
            )
        except:
            pass
    context.user_data["expect_noitem_msg"] = False
    for k in ["noitem_order_group", "noitem_user_id", "noitem_original_text", "noitem_msg_chat_id", "noitem_msg_id"]:
        context.user_data.pop(k, None)
    await update.message.reply_text(
        f"Message sent to user. Order cancelled.\nYour message: {msg}",
        parse_mode=ParseMode.HTML
    )

async def _handle_lock_qty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("expect_lock_qty"):
        return
    qty_text = update.message.text.strip()
    if not qty_text.isdigit():
        await update.message.reply_text("Please enter a valid number.")
        return
    qty = int(qty_text)
    name = context.user_data.get("lock_menu_item", "")
    if not name:
        context.user_data["expect_lock_qty"] = False
        return
    try:
        from database import set_daily_stock
        await set_daily_stock(name, qty)
        from keyboards import admin_lock_menu_inline_keyboard
        context.user_data["expect_lock_qty"] = False
        context.user_data.pop("lock_menu_item", None)
        await update.message.reply_text(
            f"✅ <b>{name}</b> limit set to {qty} for today.",
            reply_markup=await admin_lock_menu_inline_keyboard(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")
        context.user_data["expect_lock_qty"] = False


async def _text_dispatcher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Route text messages to the correct handler based on context flags."""
    if context.user_data.get("expect_item_photo"):
        await admin_photo_handle_text(update, context)
    elif context.user_data.get("expect_debt_pay_confirmation"):
        await handle_debt_pay_confirmation(update, context)
    elif context.user_data.get("expect_decline_reason"):
        await _handle_decline_reason(update, context)
    elif context.user_data.get("expect_noitem_msg"):
        await _handle_noitem_msg(update, context)
    elif context.user_data.get("expect_allow_username"):
        await _handle_allow_username(update, context)
    elif context.user_data.get("expect_payment_input"):
        await _handle_payment_input(update, context)
    elif context.user_data.get("expect_lock_qty"):
        await _handle_lock_qty(update, context)

application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, _text_dispatcher))
application.add_handler(MessageHandler(filters.PHOTO, admin_photo_handle_photo))
application.add_handler(CommandHandler("skip", admin_photo_handle_skip))
application.add_handler(CallbackQueryHandler(handle_debt_pay_callback, pattern="^debt_pay_"))
application.add_handler(CallbackQueryHandler(admin_photo_start, pattern="^aphoto_"))
application.add_handler(CallbackQueryHandler(admin_photo_remove, pattern="^aremove_photo_"))
application.add_handler(CallbackQueryHandler(admin_inline_callback, pattern="^auser_|^aban_|^aunban_|^aback_users|^adel_|^admin_add_item|^admin_add_category|^manage_cat_|^add_subitem_|^admin_back_menu|^deliver_|^ord_|^adel_allow_|^adebt_|^admin_add_allow|^admin_back_debt|^adebt_back_to_list|^adebt_filter_|^apay_|^noitem_|^lock_"))

async def _start_polling():
    await application.bot.delete_webhook()
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    await application.bot.set_chat_menu_button(
        menu_button=MenuButtonWebApp(text="Shop 🛍️", web_app=WebAppInfo(url=WEBAPP_URL))
    )
    while True:
        await asyncio.sleep(3600)

def _run_bot():
    try:
        asyncio.run(_start_polling())
    except Exception as e:
        logging.error(f"Bot polling crashed: {e}")

threading.Thread(target=_run_bot, daemon=True).start()

async def _start_pyro():
    from otp_sender import get_client
    try:
        await get_client()
        logging.info("Pyrogram client started")
    except Exception as e:
        logging.warning(f"Pyrogram not available (OTP login disabled): {e}")

def _run_pyro():
    if not PYRO_API_ID:
        logging.info("PYRO_API_ID not set, skipping Pyrogram")
        return
    try:
        asyncio.run(_start_pyro())
    except Exception as e:
        logging.error(f"Pyrogram thread crashed: {e}")

threading.Thread(target=_run_pyro, daemon=True).start()

# --- API Routes for Android App ---

@app.route("/api/auth/request-otp", methods=["POST"])
def api_request_otp():
    data = request.get_json()
    username = (data.get("username") or "").lstrip("@")
    if not username:
        return jsonify({"error": "Username required"}), 400

    user_result = asyncio.run(_db(
        lambda: database._supabase.table("users").select("user_id, full_name, banned")
        .eq("username", username).limit(1).execute()
    ))
    user = user_result.data[0] if user_result.data else None
    if user and user.get("banned"):
        return jsonify({"error": "You are banned"}), 403
    user_id = user["user_id"] if user else None

    recent = asyncio.run(_db(
        lambda: database._supabase.table("login_otps")
        .select("id")
        .eq("username", username)
        .gt("created_at", (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat())
        .execute()
    ))
    if len(recent.data) >= 3:
        return jsonify({"error": "Too many requests. Try again later."}), 429

    asyncio.run(_db(
        lambda: database._supabase.table("login_otps")
        .delete().eq("username", username).eq("used", False).execute()
    ))

    otp = str(random.randint(100000, 999999))
    expires = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
    asyncio.run(_db(
        lambda: database._supabase.table("login_otps").insert({
            "username": username, "user_id": user_id,
            "otp": otp, "expires_at": expires
        }).execute()
    ))

    sent = False

    # Try bot first (for existing users who have messaged the bot)
    if user_id:
        if _send_telegram(user_id, f"<b>Shemsu Shop Login Code</b>\n\n{otp}\n\nExpires in 5 minutes."):
            sent = True
            logging.info(f"OTP sent to user_id={user_id} via bot")

    # Fallback: try Pyrogram (for new users or if bot fails)
    if not sent:
        try:
            asyncio.run(send_otp(username, otp))
            sent = True
        except Exception as e:
            logging.error(f"Pyrogram send failed for @{username}: {e}")

    if not sent:
        return jsonify({"error": "Could not deliver OTP"}), 500

    return jsonify({"success": True, "delivery": "bot" if user_id and sent else "pyrogram"})


@app.route("/api/auth/verify-otp", methods=["POST"])
def api_verify_otp():
    data = request.get_json()
    username = (data.get("username") or "").lstrip("@")
    otp = data.get("otp", "")
    if not username or not otp:
        return jsonify({"error": "Username and OTP required"}), 400

    result = asyncio.run(_db(
        lambda: database._supabase.table("login_otps")
        .select("*")
        .eq("username", username)
        .eq("otp", otp)
        .eq("used", False)
        .gt("expires_at", datetime.now(timezone.utc).isoformat())
        .limit(1)
        .execute()
    ))
    if not result.data:
        return jsonify({"error": "Invalid or expired OTP"}), 401
    record = result.data[0]

    asyncio.run(_db(
        lambda: database._supabase.table("login_otps")
        .update({"used": True}).eq("id", record["id"]).execute()
    ))

    user_id = record["user_id"]

    # New user: resolve user_id via Pyrogram and create users row
    if not user_id:
        try:
            async def _resolve_new_user():
                from otp_sender import get_client
                client = await get_client()
                resolved = await client.get_users(username)
                return resolved.id
            user_id = asyncio.run(_resolve_new_user())
            asyncio.run(_db(
                lambda: database._supabase.table("users").upsert({
                    "user_id": user_id, "username": username,
                    "full_name": username, "banned": False
                }).execute()
            ))
            logging.info(f"Created users row for new user @{username} (user_id={user_id})")
        except Exception as e:
            logging.error(f"Failed to resolve user_id for @{username}: {e}")
            return jsonify({"error": "Could not verify identity"}), 500

    import uuid
    token = str(uuid.uuid4())
    expires = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    asyncio.run(_db(
        lambda: database._supabase.table("sessions").insert({
            "token": token, "user_id": user_id,
            "username": username, "expires_at": expires
        }).execute()
    ))

    return jsonify({"success": True, "session_token": token, "is_new_user": record["user_id"] is None})


@app.route("/api/auth/session", methods=["GET"])
def api_check_session():
    token = request.args.get("token")
    if not token:
        return jsonify({"error": "Token required"}), 400
    result = asyncio.run(_db(
        lambda: database._supabase.table("sessions")
        .select("user_id, username, expires_at")
        .eq("token", token)
        .gt("expires_at", datetime.now(timezone.utc).isoformat())
        .limit(1)
        .execute()
    ))
    if not result.data:
        return jsonify({"error": "Invalid or expired session"}), 401
    session = result.data[0]
    user_result = asyncio.run(_db(
        lambda: database._supabase.table("users")
        .select("full_name")
        .eq("user_id", session["user_id"])
        .limit(1)
        .execute()
    ))
    full_name = user_result.data[0]["full_name"] if user_result.data else ""
    return jsonify({
        "user_id": session["user_id"],
        "username": session["username"],
        "full_name": full_name
    })


@app.route("/api/user/profile", methods=["GET"])
def api_get_profile():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    result = asyncio.run(_db(
        lambda: database._supabase.table("users")
        .select("user_id, full_name, username, banned, created_at")
        .eq("user_id", int(user_id)).limit(1).execute()
    ))
    if not result.data:
        return jsonify({"error": "Not found"}), 404
    return jsonify(result.data[0])


@app.route("/api/user/profile", methods=["PUT"])
def api_update_profile():
    data = request.get_json()
    user_id = data.get("user_id")
    full_name = data.get("full_name")
    if not user_id or not full_name:
        return jsonify({"error": "user_id and full_name required"}), 400
    asyncio.run(_db(
        lambda: database._supabase.table("users")
        .update({"full_name": full_name}).eq("user_id", int(user_id)).execute()
    ))
    return jsonify({"success": True})


@app.route("/api/menu", methods=["GET"])
def api_get_menu():
    try:
        parent = request.args.get("parent")
        query = database._supabase.table("menu").select("name, price, parent, image_url")
        if parent:
            query = query.eq("parent", parent)
        query = query.order("parent", nullsfirst=True).order("name")
        result = asyncio.run(_db(lambda: query.execute()))
        enriched = []
        for idx, item in enumerate(result.data):
            enriched.append({
                "id": idx + 1,
                "name": item["name"],
                "price": float(item["price"]),
                "parent": item.get("parent"),
                "image_url": item.get("image_url") or "",
                "available": True
            })
        return jsonify(enriched)
    except Exception as e:
        logging.error(f"api_get_menu error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/api/payment-accounts", methods=["GET"])
def api_get_payment_accounts():
    result = asyncio.run(_db(
        lambda: database._supabase.table("payment_accounts")
        .select("*").order("bank_name").execute()
    ))
    return jsonify(result.data)


@app.route("/api/debt-allow-list/check", methods=["GET"])
def api_check_debt_allow():
    username = (request.args.get("username") or "").lstrip("@")
    if not username:
        return jsonify({"allowed": False})
    result = asyncio.run(_db(
        lambda: database._supabase.table("debt_allow_list")
        .select("id").eq("username", username).limit(1).execute()
    ))
    return jsonify({"allowed": len(result.data) > 0})


@app.route("/api/debts", methods=["GET"])
def api_get_debts():
    username = (request.args.get("username") or "").lstrip("@")
    if not username:
        return jsonify({"error": "username required"}), 400
    result = asyncio.run(_db(
        lambda: database._supabase.table("debts")
        .select("*")
        .eq("username", username)
        .order("created_at", desc=True)
        .limit(50).execute()
    ))
    # Android app expects a plain JSON array
    return jsonify(result.data)


@app.route("/api/debts/active-total", methods=["GET"])
def api_get_debts_active_total():
    username = (request.args.get("username") or "").lstrip("@")
    if not username:
        return jsonify({"active_total": 0.0})
    active = asyncio.run(_db(
        lambda: database._supabase.table("debts")
        .select("amount")
        .eq("username", username)
        .eq("status", "active").execute()
    ))
    active_total = sum(r["amount"] for r in active.data)
    return jsonify({"active_total": active_total})


@app.route("/api/debts/pay", methods=["POST"])
def api_pay_debt():
    data = request.get_json()
    username = (data.get("username") or "").lstrip("@")
    user_id = data.get("user_id")
    amount = data.get("amount")
    payment_account_id = data.get("payment_account_id")
    confirmation = data.get("confirmation", "")
    if not username or not user_id or not amount:
        return jsonify({"success": False, "error": "username, user_id, amount required"}), 400
    payment_info = f"account_id={payment_account_id}, confirmation={confirmation}"
    asyncio.run(database.save_debt_payment(username, int(user_id), float(amount), payment_info))
    return jsonify({"success": True})


@app.route("/api/orders", methods=["GET"])
def api_get_orders():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    result = asyncio.run(_db(
        lambda: database._supabase.table("orders")
        .select("id, item, qty, status, order_group, timestamp")
        .eq("user_id", int(user_id))
        .order("timestamp", desc=True)
        .limit(50).execute()
    ))
    return jsonify(result.data)


@app.route("/api/orders/group/<order_group>", methods=["GET"])
def api_get_order_group(order_group):
    items = asyncio.run(_db(
        lambda: database._supabase.table("orders")
        .select("id, item, qty, status, timestamp")
        .eq("order_group", order_group).execute()
    ))
    payment = asyncio.run(_db(
        lambda: database._supabase.table("order_payments")
        .select("payment_info").eq("order_group", order_group).limit(1).execute()
    ))
    comment = asyncio.run(_db(
        lambda: database._supabase.table("order_comments")
        .select("comment").eq("order_group", order_group).limit(1).execute()
    ))
    decline = asyncio.run(_db(
        lambda: database._supabase.table("order_decline_reasons")
        .select("reason").eq("order_group", order_group).limit(1).execute()
    ))
    menu = asyncio.run(_db(
        lambda: database._supabase.table("menu").select("name, price").execute()
    ))
    prices = {r["name"]: r["price"] for r in menu.data}
    total = sum((prices.get(i["item"], 0) * i["qty"]) for i in items.data)
    return jsonify({
        "order_group": order_group,
        "items": items.data,
        "total": total,
        "payment": payment.data[0]["payment_info"] if payment.data else None,
        "comment": comment.data[0]["comment"] if comment.data else None,
        "decline_reason": decline.data[0]["reason"] if decline.data else None,
        "status": items.data[0]["status"] if items.data else None,
        "created_at": items.data[0]["timestamp"] if items.data else None
    })


@app.route("/api/orders", methods=["POST"])
def api_place_order():
    data = request.get_json()
    user_id = data.get("user_id")
    username = data.get("username")
    full_name = data.get("full_name")
    items = data.get("items", [])
    payment_method = data.get("payment_method", "")
    payment_account_id = data.get("payment_account_id")
    confirmation = data.get("confirmation")
    comment = data.get("comment")
    if not user_id or not items:
        return jsonify({"success": False, "error": "user_id and items required"}), 400
    if payment_method == "debt":
        allow = asyncio.run(_db(
            lambda: database._supabase.table("debt_allow_list")
            .select("id").eq("username", (username or "").lstrip("@")).limit(1).execute()
        ))
        if not allow.data:
            return jsonify({"success": False, "error": "You are not on the debt allow list."}), 403
    order_group = f"APP-{datetime.now(timezone.utc).strftime('%y%m%d')}-{random.randint(1000,9999)}"
    for item in items:
        asyncio.run(database.save_order(
            int(user_id), item["item"], item["qty"], order_group, "Pending"
        ))
    if comment:
        asyncio.run(database.save_order_comment(order_group, comment))
    if payment_method and payment_account_id and confirmation:
        payment_info = f"{payment_method}:{payment_account_id}:{confirmation}"
        asyncio.run(database.save_order_payment(order_group, payment_info))
    # Check referral for display in notification
    ref_name = None
    ref = asyncio.run(_db(
        lambda: database._supabase.table("referrals")
        .select("referrer_id").eq("referred_id", int(user_id)).limit(1).execute()
    ))
    if ref.data:
        referrer_id = ref.data[0]["referrer_id"]
        ref_user = asyncio.run(_db(
            lambda: database._supabase.table("users")
            .select("username").eq("user_id", referrer_id).limit(1).execute()
        ))
        if ref_user.data:
            ref_name = ref_user.data[0]["username"]
    # Notify all admins
    admin_ids = asyncio.run(get_admin_user_id())
    if admin_ids:
        try:
            order_summary = "; ".join(f"{i['item']} x{i['qty']}" for i in items)
            if ref_name:
                order_summary += f" | 👤 Referred by: @{ref_name}"
            for aid in admin_ids:
                asyncio.run(_db(lambda aid=aid: database._supabase.table("notifications").insert({
                    "user_id": int(aid), "title": "New App Order",
                    "body": f"From {full_name or username}: {order_summary}"
                }).execute()))
        except Exception:
            pass
    menu_data = asyncio.run(_db(
        lambda: database._supabase.table("menu").select("name, price").execute()
    ))
    prices = {r["name"]: r["price"] for r in menu_data.data}
    total = sum(prices.get(i["item"], 0) * i["qty"] for i in items)
    return jsonify({
        "success": True,
        "order_group": order_group,
        "total": total,
        "payment_method": payment_method,
        "status": "Pending"
    })


@app.route("/api/orders/<order_group>", methods=["DELETE"])
def api_cancel_order(order_group):
    if not order_group:
        return jsonify({"success": False, "error": "order_group required"}), 400
    asyncio.run(database.cancel_order_group(order_group))
    return jsonify({"success": True})


@app.route("/api/notifications", methods=["GET"])
def api_get_notifications():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    result = asyncio.run(_db(
        lambda: database._supabase.table("notifications")
        .select("*")
        .eq("user_id", int(user_id))
        .order("created_at", desc=True)
        .limit(50).execute()
    ))
    return jsonify(result.data)


@app.route("/api/notifications/<int:nid>/read", methods=["PUT"])
def api_mark_notification_read(nid):
    asyncio.run(_db(
        lambda: database._supabase.table("notifications")
        .update({"read": True}).eq("id", nid).execute()
    ))
    return jsonify({"success": True})


@app.route("/api/feedback", methods=["POST"])
def api_submit_feedback():
    data = request.get_json()
    user_id = data.get("user_id")
    msg = data.get("msg")
    if not user_id or not msg:
        return jsonify({"error": "user_id and msg required"}), 400
    name_result = asyncio.run(_db(
        lambda: database._supabase.table("users").select("full_name").eq("user_id", int(user_id)).limit(1).execute()
    ))
    name = name_result.data[0]["full_name"] if name_result.data else "Unknown"
    asyncio.run(_db(
        lambda: database._supabase.table("feedback").insert({
            "user_id": int(user_id), "name": name, "msg": msg
        }).execute()
    ))
    return jsonify({"success": True})


@app.route("/api/referrals/stats", methods=["GET"])
def api_referral_stats():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    user_id = int(user_id)
    if user_id not in (5407307505, 7598009952):
        return jsonify({"error": "not authorized"}), 403
    count = asyncio.run(database.get_referral_count(user_id))
    points = asyncio.run(database.get_referral_points(user_id))
    earnings = asyncio.run(database.get_referral_earnings(user_id))
    return jsonify({
        "count": count,
        "points": points,
        "earnings": [
            {"items": e["items"], "earned_at": e["earned_at"],
             "referred": e.get("referred", {})}
            for e in earnings
        ]
    })


@app.route("/api/contact", methods=["POST"])
def api_contact_admin():
    data = request.get_json()
    user_id = data.get("user_id")
    username = data.get("username", "Unknown")
    message = data.get("message", "")
    if not user_id or not message:
        return jsonify({"error": "user_id and message required"}), 400
    name_result = asyncio.run(_db(
        lambda: database._supabase.table("users").select("full_name").eq("user_id", int(user_id)).limit(1).execute()
    ))
    name = name_result.data[0]["full_name"] if name_result.data else username

    # Save to feedback table so admin sees it in Feedback section
    try:
        asyncio.run(_db(
            lambda: database._supabase.table("feedback").insert({
                "user_id": int(user_id), "name": name, "msg": f"[Contact] {message}"
            }).execute()
        ))
    except Exception as e:
        logging.error(f"Contact feedback insert failed: {e}")

    # Notify admins
    admin_ids = asyncio.run(get_admin_user_id())
    if admin_ids:
        for aid in admin_ids:
            _save_notification(aid, f"📩 Contact from {name} (@{username})", message)
            _send_telegram(aid, f"<b>📩 Contact from {name}</b>\n<b>@{username}</b> (user_id: {user_id})\n\n{message}")
    return jsonify({"success": True})


@app.route("/")
def home():
    return "Bot is running."

@app.route("/health")
def health():
    return "ok"

@app.route("/api/help", methods=["GET"])
def api_get_help():
    return jsonify({
        "topics": [
            {"id": "order", "title": "How to Order", "content": "1. Tap Menu from the main menu\n2. Browse categories and select items\n3. Enter quantity\n4. Review and confirm your order\n5. Add payment info if required\n\nYour order will be sent to the admin for processing."},
            {"id": "edit_cancel", "title": "Edit / Cancel Orders", "content": "You can edit or cancel Pending orders before 6PM UTC:\n1. Go to My Orders\n2. Tap the order\n3. Choose Cancel Order\n\nAfter 6PM UTC, orders cannot be modified."},
            {"id": "debt", "title": "Debt System", "content": "Eligible users can order on debt:\n1. When ordering, select Debt as payment method\n2. The amount is added to your debt balance\n3. Pay later via My Debt section\n\nOnly whitelisted users can use the debt system."},
            {"id": "payment", "title": "Payment Methods", "content": "We accept bank transfers:\n1. Select your bank from the available accounts\n2. Transfer the exact amount shown\n3. Paste your SMS confirmation or transaction reference\n4. Admin will verify and accept your order"},
            {"id": "contact", "title": "Contact Admin", "content": f"If you need help, use the Contact Admin form or message @{ADMIN_USERNAMES[0]} directly on Telegram.\n\nThe admin will respond as soon as possible."},
        ]
    })

def _send_telegram(chat_id, text):
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
            timeout=10
        )
        if not r.ok:
            logging.error(f"Telegram send failed to {chat_id}: {r.status_code} {r.text}")
        return r.ok
    except Exception as e:
        logging.error(f"Telegram send exception to {chat_id}: {e}")
        return False

# --- Admin API endpoints ---
ADMIN_IDS = [7041035485, 5703977567]

@app.route("/api/admin/check", methods=["GET"])
def api_admin_check():
    user_id = request.args.get("user_id")
    if user_id:
        try:
            if int(user_id) in ADMIN_IDS:
                return jsonify({"admin": True})
        except: pass
    return jsonify({"admin": False})

@app.route("/api/admin/dashboard", methods=["GET"])
def api_admin_dashboard():
    pending = asyncio.run(database.get_grouped_orders_by_status("Pending", today_only=True))
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    all_today = asyncio.run(_db(lambda: database._supabase.table("orders")
        .select("order_group", count="exact")
        .gte("timestamp", today)
        .execute()))
    profit = asyncio.run(database.get_todays_profit())
    users = asyncio.run(database.get_all_users())
    return jsonify({
        "pending_orders": len(pending) if pending else 0,
        "today_orders": all_today.count or 0,
        "total_users": len(users) if users else 0,
        "today_profit": profit or 0.0
    })

@app.route("/api/admin/orders", methods=["GET"])
def api_admin_orders():
    status = request.args.get("status")
    today_only = request.args.get("today_only", "0") == "1"
    orders = asyncio.run(database.get_grouped_orders_by_status(status if status else None, today_only))
    result = []
    for g in orders:
        items_raw = asyncio.run(_db(lambda: database._supabase.table("orders")
            .select("item, qty").eq("order_group", g["order_group"]).execute()))
        user = asyncio.run(_db(lambda: database._supabase.table("users")
            .select("full_name").eq("user_id", g.get("user_id", 0)).limit(1).execute()))
        result.append({
            "order_group": g["order_group"],
            "status": g.get("status", "Pending"),
            "user_name": user.data[0]["full_name"] if user.data else None,
            "user_id": g.get("user_id"),
            "items": items_raw.data,
            "total": g.get("total", 0),
            "timestamp": g.get("timestamp", "")
        })
    return jsonify(result)

@app.route("/api/admin/orders/<order_group>/accept", methods=["POST"])
def api_admin_accept(order_group):
    asyncio.run(database.update_order_status(order_group, "Accepted"))
    og = asyncio.run(_db(lambda: database._supabase.table("orders")
        .select("*").eq("order_group", order_group).limit(1).execute()))
    if og.data:
        uid = og.data[0].get("user_id")
        if uid:
            _send_telegram(uid, "<b>Order Accepted!</b>\n\nYour order is being prepared.")
            _save_notification(uid, "Order Accepted", "Your order is being prepared.")
    return jsonify({"success": True})

@app.route("/api/admin/orders/<order_group>/decline", methods=["POST"])
def api_admin_decline(order_group):
    data = request.get_json()
    reason = data.get("reason", "No reason provided")
    asyncio.run(database.update_order_status(order_group, "Declined"))
    asyncio.run(database.save_order_decline_reason(order_group, reason))
    og = asyncio.run(_db(lambda: database._supabase.table("orders")
        .select("*").eq("order_group", order_group).limit(1).execute()))
    if og.data:
        uid = og.data[0].get("user_id")
        if uid:
            _send_telegram(uid, f"<b>Order Declined</b>\n\n<b>Reason:</b> {reason}\n\nContact @{ADMIN_USERNAMES[0]} if you have questions.")
            _save_notification(uid, "Order Declined", f"Reason: {reason}")
    return jsonify({"success": True})

@app.route("/api/admin/orders/<order_group>/ready", methods=["POST"])
def api_admin_ready(order_group):
    asyncio.run(database.update_order_status(order_group, "Ready"))
    og = asyncio.run(_db(lambda: database._supabase.table("orders")
        .select("*").eq("order_group", order_group).limit(1).execute()))
    if og.data:
        uid = og.data[0].get("user_id")
        if uid:
            _send_telegram(uid, "<b>Order Ready!</b>\n\nYour order is ready for pickup/delivery.")
            _save_notification(uid, "Order Ready", "Your order is ready for pickup/delivery.")
    return jsonify({"success": True})

@app.route("/api/admin/orders/<order_group>/deliver", methods=["POST"])
def api_admin_deliver(order_group):
    data = request.get_json()
    dtype = data.get("type", "paid")
    og = asyncio.run(_db(lambda: database._supabase.table("orders")
        .select("*").eq("order_group", order_group).execute()))
    asyncio.run(database.update_order_status(order_group, "Delivered"))
    if og.data:
        uid = og.data[0].get("user_id")
        user = asyncio.run(_db(lambda: database._supabase.table("users")
            .select("username, full_name").eq("user_id", uid).limit(1).execute()))
        uname = user.data[0]["username"] if user.data else "unknown"
        fname = user.data[0]["full_name"] if user.data else "Unknown"
        total = sum(r.get("qty", 0) * (_get_price(r["item"]) or 0) for r in og.data)
        if dtype == "debt":
            desc = "; ".join(f"{r['qty']}x {r['item']}" for r in og.data)
            asyncio.run(database.add_debt(uname, total, desc, order_group, uid, fname))
        # Record referral earning on delivery
        if uid:
            ref = asyncio.run(_db(lambda: database._supabase.table("referrals")
                .select("referrer_id").eq("referred_id", uid).limit(1).execute()))
            if ref.data:
                referrer_id = ref.data[0]["referrer_id"]
                items_summary = "; ".join(f"{r['item']} x{r['qty']}" for r in og.data)
                asyncio.run(database.record_referral_earning(referrer_id, uid, order_group, items_summary))
            status_text = "Paid" if dtype == "paid" else "Added to debt"
            _send_telegram(uid, f"<b>Order Delivered</b>\n\nStatus: {status_text}")
            _save_notification(uid, "Order Delivered", f"Delivered - {status_text}")
    return jsonify({"success": True})

def _save_notification(user_id, title, body):
    try:
        asyncio.run(_db(lambda: database._supabase.table("notifications").insert({
            "user_id": int(user_id), "title": title, "body": body
        }).execute()))
    except Exception as e:
        logging.error(f"Notification insert failed for user {user_id}: {e}")

def _get_price(item_name):
    m = asyncio.run(_db(lambda: database._supabase.table("menu")
        .select("price").eq("name", item_name).limit(1).execute()))
    return m.data[0]["price"] if m.data else 0

@app.route("/api/admin/menu", methods=["GET"])
def api_admin_menu():
    items = asyncio.run(database.get_all_menu_items())
    return jsonify(items)

@app.route("/api/admin/menu", methods=["POST"])
def api_admin_add_menu():
    data = request.get_json()
    name = data.get("name")
    price = data.get("price", 0)
    parent = data.get("parent")
    image_url = data.get("image_url")
    if not name: return jsonify({"error": "name required"}), 400
    asyncio.run(database.add_menu_item(name, float(price), parent))
    if image_url: asyncio.run(database.update_menu_image(name, image_url))
    return jsonify({"success": True})

@app.route("/api/admin/menu/<path:item_name>", methods=["PUT"])
def api_admin_update_menu(item_name):
    data = request.get_json()
    name = data.get("name")
    price = data.get("price")
    parent = data.get("parent")
    image_url = data.get("image_url")
    if name and name != item_name:
        asyncio.run(_db(lambda: database._supabase.table("menu")
            .update({"name": name}).eq("name", item_name).execute()))
    updates = {}
    if price is not None: updates["price"] = float(price)
    if parent is not None: updates["parent"] = parent if parent else None
    if image_url is not None: updates["image_url"] = image_url if image_url else None
    if updates:
        asyncio.run(_db(lambda: database._supabase.table("menu")
            .update(updates).eq("name", name or item_name).execute()))
    return jsonify({"success": True})

@app.route("/api/admin/menu/<path:item_name>", methods=["DELETE"])
def api_admin_delete_menu(item_name):
    asyncio.run(database.delete_menu_item(item_name))
    return jsonify({"success": True})

@app.route("/api/admin/stock", methods=["GET"])
def api_admin_stock():
    stocks = asyncio.run(database.get_all_daily_stocks())
    return jsonify(stocks)

@app.route("/api/admin/stock/<path:name>", methods=["PUT"])
def api_admin_set_stock(name):
    data = request.get_json()
    max_qty = data.get("max_qty", 0)
    asyncio.run(database.set_daily_stock(name, int(max_qty)))
    return jsonify({"success": True})

@app.route("/api/admin/stock/<path:name>/toggle-lock", methods=["POST"])
def api_admin_toggle_lock(name):
    stock = asyncio.run(database.get_daily_stock(name))
    locked = not (stock.get("locked") if stock else False)
    asyncio.run(database.toggle_lock_daily_stock(name, locked))
    return jsonify({"success": True, "locked": locked})

@app.route("/api/admin/stock/<path:name>", methods=["DELETE"])
def api_admin_clear_stock(name):
    asyncio.run(database.clear_daily_stock(name))
    return jsonify({"success": True})

@app.route("/api/admin/stock/unlock-all", methods=["POST"])
def api_admin_unlock_all():
    items = asyncio.run(database.get_all_menu_items())
    for i in items:
        if i.get("price", 0) > 0:
            asyncio.run(database.clear_daily_stock(i["name"]))
    return jsonify({"success": True})

@app.route("/api/admin/debts", methods=["GET"])
def api_admin_debts():
    filter_type = request.args.get("filter", "active")
    debts = asyncio.run(database.get_all_debts(filter_type))
    return jsonify(debts)

@app.route("/api/admin/debts/<int:debt_id>/pay", methods=["POST"])
def api_admin_debt_pay(debt_id):
    asyncio.run(database.mark_debt_paid(debt_id))
    return jsonify({"success": True})

@app.route("/api/admin/debts/<int:debt_id>/waive", methods=["POST"])
def api_admin_debt_waive(debt_id):
    asyncio.run(database.waive_debt(debt_id))
    return jsonify({"success": True})

@app.route("/api/admin/debt-allow-list", methods=["GET"])
def api_admin_allow_list():
    entries = asyncio.run(database.get_debt_allow_list())
    return jsonify(entries)

@app.route("/api/admin/debt-allow-list", methods=["POST"])
def api_admin_add_allow():
    data = request.get_json()
    username = data.get("username", "").lstrip("@")
    if not username: return jsonify({"error": "username required"}), 400
    asyncio.run(database.add_to_debt_allow_list(username, "webapp"))
    return jsonify({"success": True})

@app.route("/api/admin/debt-allow-list/<path:username>", methods=["DELETE"])
def api_admin_remove_allow(username):
    asyncio.run(database.remove_from_debt_allow_list(username))
    return jsonify({"success": True})

@app.route("/api/admin/payment-accounts", methods=["GET"])
def api_admin_payment_accounts():
    accounts = asyncio.run(database.get_payment_accounts())
    return jsonify(accounts)

@app.route("/api/admin/payment-accounts", methods=["POST"])
def api_admin_add_payment():
    data = request.get_json()
    bank_name = data.get("bank_name")
    number = data.get("number")
    holder_name = data.get("holder_name", "")
    if not bank_name or not number: return jsonify({"error": "bank_name and number required"}), 400
    asyncio.run(database.add_payment_account(bank_name, number, holder_name))
    return jsonify({"success": True})

@app.route("/api/admin/payment-accounts/<int:pid>", methods=["DELETE"])
def api_admin_delete_payment(pid):
    asyncio.run(database.delete_payment_account(pid))
    return jsonify({"success": True})

@app.route("/api/admin/users", methods=["GET"])
def api_admin_users():
    users = asyncio.run(database.get_all_users_detailed())
    return jsonify(users)

@app.route("/api/admin/users/<int:uid>/ban", methods=["POST"])
def api_admin_ban(uid):
    asyncio.run(database.ban_user(uid))
    _send_telegram(uid, "<b>You have been banned.</b>")
    return jsonify({"success": True})

@app.route("/api/admin/users/<int:uid>/unban", methods=["POST"])
def api_admin_unban(uid):
    asyncio.run(database.unban_user(uid))
    _send_telegram(uid, "<b>You have been unbanned.</b>")
    return jsonify({"success": True})

@app.route("/api/admin/broadcast", methods=["POST"])
def api_admin_broadcast():
    data = request.get_json()
    message = data.get("message", "")
    if not message: return jsonify({"error": "message required"}), 400
    users = asyncio.run(database.get_all_users())
    sent = 0
    for (uid,) in users:
        if _send_telegram(uid, f"<b>Broadcast</b>\n\n{message}"):
            sent += 1
    return jsonify({"success": True, "sent": sent})

@app.route("/api/admin/feedback", methods=["GET"])
def api_admin_feedback():
    feedback = asyncio.run(database.get_all_feedback())
    return jsonify(feedback)

@app.route("/api/admin/referrals/earnings", methods=["GET"])
def api_admin_referral_earnings():
    earnings = asyncio.run(_db(
        lambda: database._supabase.table("referral_earnings")
        .select("*").order("earned_at", desc=True).execute()
    ))
    result = []
    for e in earnings.data:
        referrer = asyncio.run(_db(
            lambda: database._supabase.table("users")
            .select("username, full_name").eq("user_id", e["referrer_id"]).limit(1).execute()
        ))
        referred = asyncio.run(_db(
            lambda: database._supabase.table("users")
            .select("username, full_name").eq("user_id", e["referred_id"]).limit(1).execute()
        ))
        result.append({
            "id": e["id"],
            "referrer_id": e["referrer_id"],
            "referred_id": e["referred_id"],
            "order_group": e["order_group"],
            "items": e["items"],
            "earned_at": e["earned_at"],
            "referrer_username": referrer.data[0]["username"] if referrer.data else None,
            "referrer_name": referrer.data[0]["full_name"] if referrer.data else None,
            "referred_username": referred.data[0]["username"] if referred.data else None,
            "referred_name": referred.data[0]["full_name"] if referred.data else None,
        })
    return jsonify(result)


# --- Webapp static files ---
_webapp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "webapp")

@app.route("/app/admin/")
@app.route("/app/admin/<path:filename>")
def webapp_admin_static(filename="admin.html"):
    admin_dir = os.path.join(_webapp_dir, "admin")
    admin_path = os.path.join(admin_dir, filename)
    if os.path.isfile(admin_path):
        return send_from_directory(admin_dir, filename)
    webapp_path = os.path.join(_webapp_dir, filename)
    if os.path.isfile(webapp_path):
        return send_from_directory(_webapp_dir, filename)
    return send_from_directory(_webapp_dir, "admin.html")

@app.route("/app/")
@app.route("/app/<path:filename>")
def webapp_static(filename="index.html"):
    filepath = os.path.join(_webapp_dir, filename)
    if os.path.isfile(filepath):
        return send_from_directory(_webapp_dir, filename)
    return send_from_directory(_webapp_dir, "index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
