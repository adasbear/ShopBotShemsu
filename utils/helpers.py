from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from config import ADMIN_USERNAME
from database import get_user
from keyboards import get_banned_keyboard

BAN_MESSAGE = (
    "<b>You have been banned</b>\n\n"
    "You have violated one or more of our rules so you are banned.\n"
    f"If you believe this was a mistake, contact @{ADMIN_USERNAME} or use the <b>Contact Admin</b> button below."
)

def is_admin(username):
    return username == ADMIN_USERNAME

async def check_banned(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.effective_user.id
    user = await get_user(user_id)
    if user and user.get("banned"):
        if not context.user_data.get("_banned_sent"):
            await update.effective_user.send_message(
                BAN_MESSAGE,
                reply_markup=get_banned_keyboard(),
                parse_mode="HTML"
            )
            context.user_data["_banned_sent"] = True
        return True
    return False

def build_order_summary(items):
    total = sum(i["qty"] * i["price"] for i in items)
    lines = []
    for i in items:
        lines.append(f"{i['qty']}x {i['item']} - Birr {i['qty']*i['price']:.2f}")
    return "\n".join(lines), total

def build_admin_order_text(user_name, items):
    summary, total = build_order_summary(items)
    text = f"NEW ORDER FROM: {user_name}\n\n{summary}\n\nTOTAL: Birr {total:.2f}"
    return text, total
