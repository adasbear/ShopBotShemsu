import sqlite3
import logging
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    CallbackQueryHandler, filters, ContextTypes, ConversationHandler
)

# --- CONFIGURATION ---
TOKEN = "8783688125:AAEBGTQYkDEo925gQXslKSX2atPl6IDuf7k"
ADMIN_ID = 5970769337

# States
REGISTRATION, MENU_SELECTION, QTY_INPUT, ADD_MORE_PROMPT, CONFIRM_ORDER, BROADCAST_TEXT, GIVING_FEEDBACK = range(7)

# Menu with Prices
FOOD_MENU = {
    "🍔 Burger": 5.0, "🍕 Pizza": 8.0, "🍟 Fries": 2.5, "🥤 Coke": 1.5, "🧃 Juice": 2.0
}

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('food_bot.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (user_id INTEGER PRIMARY KEY, full_name TEXT, username TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS orders 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, 
                  item TEXT, qty INTEGER, status TEXT, timestamp DATETIME)''')
    c.execute('''CREATE TABLE IF NOT EXISTS feedback 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, name TEXT, msg TEXT)''')
    conn.commit()
    conn.close()

# --- KEYBOARDS ---
def get_main_keyboard(user_id):
    buttons = [
        ["🍽 Menu", "👤 Profile"], 
        ["🧾 My Orders", "💬 Feedback"],
        ["📋 Commands"]
    ]
    if user_id == ADMIN_ID:
        buttons.append(["⚙️ Admin Panel"])
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

# --- BROADCAST LOGIC (FIXED) ---
async def perform_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END

    broadcast_msg = update.message.text
    conn = sqlite3.connect('food_bot.db')
    users = conn.execute("SELECT user_id FROM users").fetchall()
    conn.close()

    count = 0
    await update.message.reply_text(f"🚀 Starting broadcast to {len(users)} users...")

    for (uid,) in users:
        try:
            await context.bot.send_message(
                chat_id=uid, 
                text=f"📢 **ANNOUNCEMENT**\n\n{broadcast_msg}",
                parse_mode="Markdown"
            )
            count += 1
        except Exception as e:
            print(f"Could not send to {uid}: {e}")

    await update.message.reply_text(f"✅ Broadcast complete. Sent to {count} users.", reply_markup=get_main_keyboard(ADMIN_ID))
    return ConversationHandler.END

# --- FEEDBACK SYSTEM ---
async def start_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please type your feedback or suggestions:")
    return GIVING_FEEDBACK

async def save_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    msg = update.message.text
    conn = sqlite3.connect('food_bot.db')
    user_data = conn.execute("SELECT full_name FROM users WHERE user_id=?", (user_id,)).fetchone()
    name = user_data[0] if user_data else "Unknown"
    conn.execute("INSERT INTO feedback (user_id, name, msg) VALUES (?, ?, ?)", (user_id, name, msg))
    conn.commit()
    conn.close()
    
    await update.message.reply_text("Thank you for your feedback! ❤️", reply_markup=get_main_keyboard(user_id))
    await context.bot.send_message(ADMIN_ID, f"💬 **NEW FEEDBACK from {name}:**\n{msg}")
    return ConversationHandler.END

# --- ORDERING FLOW ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conn = sqlite3.connect('food_bot.db')
    user = conn.execute("SELECT full_name FROM users WHERE user_id=?", (user_id,)).fetchone()
    conn.close()

    if not user:
        await update.message.reply_text("Welcome! Enter your **Full Name** to register:")
        return REGISTRATION
    
    await update.message.reply_text(f"Welcome back, {user[0]}!", reply_markup=get_main_keyboard(user_id))
    return ConversationHandler.END

async def register_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    full_name = update.message.text
    conn = sqlite3.connect('food_bot.db')
    conn.execute("INSERT OR REPLACE INTO users VALUES (?, ?, ?)", (user_id, full_name, update.effective_user.username))
    conn.commit()
    conn.close()
    await update.message.reply_text(f"Registered!", reply_markup=get_main_keyboard(user_id))
    return ConversationHandler.END

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['session_items'] = [] # Reset session
    kb = [[InlineKeyboardButton(f"{k} - ${v}", callback_data=f"order_{k}")] for k, v in FOOD_MENU.items()]
    await update.message.reply_text("Select an item:", reply_markup=InlineKeyboardMarkup(kb))
    return MENU_SELECTION

async def handle_menu_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['current_item'] = query.data.replace("order_", "")
    await query.edit_message_text(f"How many {context.user_data['current_item']}?")
    return QTY_INPUT

async def handle_qty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    qty = update.message.text
    if not qty.isdigit():
        await update.message.reply_text("Enter a number.")
        return QTY_INPUT
    
    item = context.user_data['current_item']
    context.user_data['session_items'].append({'item': item, 'qty': int(qty), 'price': FOOD_MENU[item]})
    
    total = sum(i['qty'] * i['price'] for i in context.user_data['session_items'])
    kb = [[InlineKeyboardButton("➕ Add More", callback_data="add_more")],
          [InlineKeyboardButton(f"✅ Review & Confirm (${total:.2f})", callback_data="review")]]
    await update.message.reply_text(f"Added {qty}x {item}.", reply_markup=InlineKeyboardMarkup(kb))
    return ADD_MORE_PROMPT

async def review_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "add_more":
        kb = [[InlineKeyboardButton(f"{k}", callback_data=f"order_{k}")] for k in FOOD_MENU.keys()]
        await query.edit_message_text("Select another item:", reply_markup=InlineKeyboardMarkup(kb))
        return MENU_SELECTION
    
    summary = "🛒 **ORDER REVIEW**\n\n"
    total = 0
    for i in context.user_data['session_items']:
        cost = i['qty'] * i['price']
        total += cost
        summary += f"• {i['qty']}x {i['item']} - ${cost:.2f}\n"
    summary += f"\n💰 **TOTAL: ${total:.2f}**\nConfirm?"
    
    kb = [[InlineKeyboardButton("🚀 CONFIRM", callback_data="confirm")], [InlineKeyboardButton("❌ CANCEL", callback_data="cancel")]]
    await query.edit_message_text(summary, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
    return CONFIRM_ORDER

async def finalize_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "cancel":
        await query.edit_message_text("Cancelled.")
        return ConversationHandler.END

    user_id = update.effective_user.id
    conn = sqlite3.connect('food_bot.db')
    user_name = conn.execute("SELECT full_name FROM users WHERE user_id=?", (user_id,)).fetchone()[0]
    
    for i in context.user_data['session_items']:
        conn.execute("INSERT INTO orders (user_id, item, qty, status, timestamp) VALUES (?, ?, ?, ?, ?)",
                     (user_id, i['item'], i['qty'], "Pending", datetime.now()))
    conn.commit()
    conn.close()

    await query.edit_message_text("✅ Order placed successfully!")
    await context.bot.send_message(ADMIN_ID, f"🔔 **NEW ORDER: {user_name}**")
    return ConversationHandler.END

# --- ADMIN ACTIONS ---
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    kb = [[InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")],
          [InlineKeyboardButton("✅ Mark ALL Arrived", callback_data="admin_all_arrived")]]
    await update.message.reply_text("🛠 Admin Panel:", reply_markup=InlineKeyboardMarkup(kb))

async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "admin_broadcast":
        await query.edit_message_text("🎤 Enter the message you want to send to ALL users:")
        return BROADCAST_TEXT
    
    if query.data == "admin_all_arrived":
        conn = sqlite3.connect('food_bot.db')
        users = conn.execute("SELECT DISTINCT user_id FROM orders WHERE status='Pending'").fetchall()
        conn.execute("UPDATE orders SET status='Arrived' WHERE status='Pending'")
        conn.commit()
        conn.close()
        for (uid,) in users:
            try: await context.bot.send_message(uid, "🎁 **Your order has arrived! Come and get it!** 🏃‍♂️💨")
            except: pass
        await query.edit_message_text("✅ All users notified.")
        return ConversationHandler.END

# --- MAIN ---
def main():
    init_db()
    app = Application.builder().token(TOKEN).build()
    
    conv = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            MessageHandler(filters.Regex("^🍽 Menu$"), show_menu),
            MessageHandler(filters.Regex("^⚙️ Admin Panel$"), admin_panel),
            MessageHandler(filters.Regex("^💬 Feedback$"), start_feedback),
            MessageHandler(filters.Regex("^👤 Profile$"), start),
        ],
        states={
            REGISTRATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_user)],
            MENU_SELECTION: [CallbackQueryHandler(handle_menu_selection)],
            QTY_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_qty)],
            ADD_MORE_PROMPT: [CallbackQueryHandler(review_order)],
            CONFIRM_ORDER: [CallbackQueryHandler(finalize_order)],
            GIVING_FEEDBACK: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_feedback)],
            BROADCAST_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, perform_broadcast)],
        },
        fallbacks=[CommandHandler('start', start)],
    )

    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(admin_callback, pattern="^admin_"))
    
    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()