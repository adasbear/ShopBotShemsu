import time
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler

from config import MENU_SELECTION, QTY_INPUT, ADD_MORE_PROMPT, CONFIRM_ORDER, COMMENT_CHOICE, ORDER_COMMENT, DEBT_CHOICE
from database import get_menu, save_order, get_user, get_admin_user_id, has_sub_items, _db
from keyboards import menu_inline_keyboard, add_more_or_review_keyboard, confirm_cancel_keyboard, order_accept_decline_keyboard, comment_choice_keyboard, debt_choice_keyboard
from utils.helpers import build_order_summary, check_banned

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_banned(update, context):
        return ConversationHandler.END
    context.user_data["session_items"] = []
    await update.message.reply_text(
        "SELECT ITEMS",
        reply_markup=await menu_inline_keyboard(),
        parse_mode=ParseMode.HTML
    )
    return MENU_SELECTION

async def handle_menu_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    item = query.data.replace("order_", "")
    if item == "back_to_main":
        context.user_data.pop("menu_parent", None)
        await query.edit_message_text(
            "SELECT ITEMS",
            reply_markup=await menu_inline_keyboard(),
            parse_mode=ParseMode.HTML
        )
        return MENU_SELECTION
    if item == "back":
        items = context.user_data.get("session_items", [])
        if items:
            _, total = build_order_summary(items)
            await query.edit_message_text(
                "Back to order review.",
                reply_markup=add_more_or_review_keyboard(total)
            )
            return ADD_MORE_PROMPT
        await query.edit_message_text("Order Cancelled.")
        return ConversationHandler.END
    if await has_sub_items(item):
        await query.edit_message_text(
            f"SELECT {item.upper()}",
            reply_markup=await menu_inline_keyboard(parent=item),
            parse_mode=ParseMode.HTML
        )
        return MENU_SELECTION
    from database import is_item_available_today
    if not await is_item_available_today(item):
        await query.edit_message_text(
            f"❌ <b>{item}</b> is sold out for today.",
            parse_mode=ParseMode.HTML
        )
        return MENU_SELECTION
    context.user_data["current_item"] = item
    await query.edit_message_text(
        f"How many <b>{item}</b>?",
        parse_mode=ParseMode.HTML
    )
    return QTY_INPUT

async def handle_qty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    qty = update.message.text
    if not qty.isdigit() or int(qty) == 0:
        await update.message.reply_text("Enter a valid number greater than 0.")
        return QTY_INPUT

    item = context.user_data["current_item"]
    menu = await get_menu()
    price = menu[item]

    context.user_data["session_items"].append({
        "item": item, "qty": int(qty), "price": price
    })

    _, total = build_order_summary(context.user_data["session_items"])
    await update.message.reply_text(
        f"Added {qty}x {item}.",
        reply_markup=add_more_or_review_keyboard(total)
    )
    return ADD_MORE_PROMPT

async def review_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "add_more":
        await query.edit_message_text(
            "Select another item:",
            reply_markup=await menu_inline_keyboard()
        )
        return MENU_SELECTION

    summary, total = build_order_summary(context.user_data["session_items"])
    text = f"FINAL ORDER REVIEW\n\n{summary}\n\nTOTAL: Birr {total:.2f}\n\nConfirm order?"

    await query.edit_message_text(
        text,
        reply_markup=confirm_cancel_keyboard(),
        parse_mode=ParseMode.HTML
    )
    return CONFIRM_ORDER

async def finalize_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "cancel":
        await query.edit_message_text("Order Cancelled.")
        return ConversationHandler.END

    user_id = update.effective_user.id
    user = await get_user(user_id)
    user_name = user["full_name"] if user else "Unknown"

    order_group = f"{user_id}_{int(time.time()*1000)}"
    items = context.user_data.get("session_items", [])
    total_cost = 0
    item_lines = []

    for i in items:
        cost = i["qty"] * i["price"]
        total_cost += cost
        if i.get("custom"):
            item_lines.append(f"{i['qty']}x {i['item']} (Custom request)")
        else:
            item_lines.append(f"{i['qty']}x {i['item']} (Birr {cost:.2f})")

    context.user_data["user_id"] = user_id
    context.user_data["order_group"] = order_group
    context.user_data["order_name"] = user_name
    context.user_data["order_items"] = item_lines
    context.user_data["order_total"] = total_cost

    await query.edit_message_text(
        "How would you like to pay?",
        reply_markup=debt_choice_keyboard(),
        parse_mode=ParseMode.HTML
    )
    return DEBT_CHOICE

async def handle_comment_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "skip_comment":
        await query.edit_message_text("Order submitted successfully and payment info is awaiting approval.")
        if not context.user_data.get("on_debt"):
            await _notify_admin(context)
        return ConversationHandler.END

    await query.edit_message_text("Type your special instructions below:")
    return ORDER_COMMENT

async def handle_order_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    comment = update.message.text.strip()
    if not comment:
        await update.message.reply_text("Please type your instructions or send /cancel.")
        return ORDER_COMMENT

    from database import save_order_comment
    await save_order_comment(context.user_data["order_group"], comment)
    context.user_data["order_comment"] = comment

    await update.message.reply_text("Order submitted successfully and payment info is awaiting approval.")
    if not context.user_data.get("on_debt"):
        await _notify_admin(context)
    return ConversationHandler.END

async def _notify_admin(context):
    from database import get_admin_user_id, get_referral_count, record_referral_earning, _db
    admin_ids = await get_admin_user_id()
    if not admin_ids:
        return
    comment = context.user_data.get("order_comment")
    payment = context.user_data.get("payment_info")
    user_id = context.user_data.get("user_id")
    text = (
        f"<b>NEW ORDER FROM: {context.user_data['order_name']}</b>\n\n"
        f"{chr(10).join(context.user_data['order_items'])}\n\n"
        f"TOTAL: Birr {context.user_data['order_total']:.2f}"
    )
    if payment:
        text += f"\n\n<b>Payment:</b>\n{payment}"
    if comment:
        text += f"\n\n<b>Comment:</b> {comment}"
    if user_id:
        ref = await _db(lambda: _supabase.table("referrals")
            .select("referrer_id").eq("referred_id", user_id).limit(1).execute())
        if ref.data:
            referrer_id = ref.data[0]["referrer_id"]
            ref_user = await _db(lambda: _supabase.table("users")
                .select("username").eq("user_id", referrer_id).limit(1).execute())
            ref_username = ref_user.data[0]["username"] if ref_user.data else str(referrer_id)
            text += f"\n\n👤 <b>Referred by:</b> @{ref_username}"
            items_summary = "; ".join(context.user_data.get("order_items", []))
            await record_referral_earning(referrer_id, user_id, context.user_data["order_group"], items_summary)
    for admin_id in admin_ids:
        await context.bot.send_message(
            chat_id=admin_id,
            text=text,
            reply_markup=order_accept_decline_keyboard(context.user_data["order_group"]),
            parse_mode=ParseMode.HTML
        )
    if payment:
        text += f"\n\n<b>Payment:</b>\n{payment}"
    if comment:
        text += f"\n\n<b>Comment:</b> {comment}"
    if user_id:
        ref = await _db(lambda: _supabase.table("referrals")
            .select("referrer_id").eq("referred_id", user_id).limit(1).execute())
        if ref.data:
            referrer_id = ref.data[0]["referrer_id"]
            ref_user = await _db(lambda: _supabase.table("users")
                .select("username").eq("user_id", referrer_id).limit(1).execute())
            ref_username = ref_user.data[0]["username"] if ref_user.data else str(referrer_id)
            text += f"\n\n👤 <b>Referred by:</b> @{ref_username}"
            items_summary = "; ".join(context.user_data.get("order_items", []))
            await record_referral_earning(referrer_id, user_id, context.user_data["order_group"], items_summary)
    await context.bot.send_message(
        chat_id=admin_id,
        text=text,
        reply_markup=order_accept_decline_keyboard(context.user_data["order_group"]),
        parse_mode=ParseMode.HTML
    )
