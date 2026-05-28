import sqlite3
import logging
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
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
    c.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, full_name TEXT, username TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, item TEXT, qty INTEGER, status TEXT, timestamp DATETIME)')
    c.execute('CREATE TABLE IF NOT EXISTS feedback (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, name TEXT, msg TEXT)')
    conn.commit()
    conn.close()

# --- KEYBOARDS ---
def get_main_keyboard(user_id):
    buttons = [["🍽 Menu", "👤 Profile"], ["🧾 My Orders", "💬 Feedback"], ["📋 Commands"]]
    if user_id == ADMIN_ID:
        buttons.append(["⚙️ Admin Panel"])
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

# --- START & REGISTRATION ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conn = sqlite3.connect('food_bot.db')
    user = conn.execute("SELECT full_name FROM users WHERE user_id=?", (user_id,)).fetchone()
    conn.close()

    if not user:
        await update.message.reply_text("Welcome! Please enter your <b>Full Name</b> to register:", parse_mode=ParseMode.HTML)
        return REGISTRATION
    
    await update.message.reply_text(f"Welcome back, <b>{user[0]}</b>!", reply_markup=get_main_keyboard(user_id), parse_mode=ParseMode.HTML)
    return ConversationHandler.END

async def register_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    full_name = update.message.text
    conn = sqlite3.connect('food_bot.db')
    conn.execute("INSERT OR REPLACE INTO users VALUES (?, ?, ?)", (user_id, full_name, update.effective_user.username))
    conn.commit()
    conn.close()
    await update.message.reply_text("✅ Registration successful!", reply_markup=get_main_keyboard(user_id))
    return ConversationHandler.END

# --- MY ORDERS (USER) ---
async def view_my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conn = sqlite3.connect('food_bot.db')
    orders = conn.execute("SELECT item, qty, status, timestamp FROM orders WHERE user_id=? ORDER BY timestamp DESC LIMIT 10", (user_id,)).fetchall()
    conn.close()

    if not orders:
        await update.message.reply_text("❌ You have no orders yet.")
        return

    msg = "<b>🧾 YOUR RECENT ORDERS</b>\n\n"
    for item, qty, status, ts in orders:
        status_icon = "⏳" if status == "Pending" else "✅"
        msg += f"{status_icon} <b>{item}</b> (x{qty})\nStatus: {status}\nDate: {ts[:16]}\n\n"
    
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- FEEDBACK ---
async def start_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📝 Please type your feedback or suggestions below:")
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
    await update.message.reply_text("❤️ Thank you for your feedback!", reply_markup=get_main_keyboard(user_id))
    await context.bot.send_message(ADMIN_ID, f"💬 <b>NEW FEEDBACK from {name}:</b>\n<i>{msg}</i>", parse_mode=ParseMode.HTML)
    return ConversationHandler.END

# --- ORDERING FLOW ---
async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['session_items'] = []
    kb = [[InlineKeyboardButton(f"{k} - ${v}", callback_data=f"order_{k}")] for k, v in FOOD_MENU.items()]
    await update.message.reply_text("<b>🍴 SELECT ITEMS</b>", reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)
    return MENU_SELECTION

async def handle_menu_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['current_item'] = query.data.replace("order_", "")
    await query.edit_message_text(f"🔢 How many <b>{context.user_data['current_item']}</b>?", parse_mode=ParseMode.HTML)
    return QTY_INPUT

async def handle_qty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    qty = update.message.text
    if not qty.isdigit():
        await update.message.reply_text("⚠️ Enter a valid number.")
        return QTY_INPUT
    
    item = context.user_data['current_item']
    context.user_data['session_items'].append({'item': item, 'qty': int(qty), 'price': FOOD_MENU[item]})
    total = sum(i['qty'] * i['price'] for i in context.user_data['session_items'])
    
    kb = [[InlineKeyboardButton("➕ Add More", callback_data="add_more")],
          [InlineKeyboardButton(f"✅ Review Order (${total:.2f})", callback_data="review")]]
    await update.message.reply_text(f"Added {qty}x {item}.", reply_markup=InlineKeyboardMarkup(kb))
    return ADD_MORE_PROMPT

async def review_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "add_more":
        kb = [[InlineKeyboardButton(f"{k}", callback_data=f"order_{k}")] for k in FOOD_MENU.keys()]
        await query.edit_message_text("Select another item:", reply_markup=InlineKeyboardMarkup(kb))
        return MENU_SELECTION
    
    summary = "<b>🛒 FINAL ORDER REVIEW</b>\n\n"
    total = sum(i['qty'] * i['price'] for i in context.user_data['session_items'])
    for i in context.user_data['session_items']:
        summary += f"• {i['qty']}x {i['item']} - <i>${i['qty']*i['price']:.2f}</i>\n"
    summary += f"\n<b>💰 TOTAL TO PAY: ${total:.2f}</b>\n\nConfirm order?"
    
    kb = [[InlineKeyboardButton("🚀 CONFIRM", callback_data="confirm")], [InlineKeyboardButton("❌ CANCEL", callback_data="cancel")]]
    await query.edit_message_text(summary, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)
    return CONFIRM_ORDER

async def finalize_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "cancel":
        await query.edit_message_text("❌ Order Cancelled.")
        return ConversationHandler.END

    user_id = update.effective_user.id
    conn = sqlite3.connect('food_bot.db')
    user_name = conn.execute("SELECT full_name FROM users WHERE user_id=?", (user_id,)).fetchone()[0]
    for i in context.user_data['session_items']:
        conn.execute("INSERT INTO orders (user_id, item, qty, status, timestamp) VALUES (?, ?, ?, ?, ?)",
                     (user_id, i['item'], i['qty'], "Pending", datetime.now()))
    conn.commit()
    conn.close()

    await query.edit_message_text("✅ <b>Order Placed!</b> We will notify you when it arrives.", parse_mode=ParseMode.HTML)
    await context.bot.send_message(ADMIN_ID, f"🔔 <b>NEW ORDER:</b> {user_name}", parse_mode=ParseMode.HTML)
    return ConversationHandler.END

# --- ADMIN FUNCTIONS ---
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    kb = [
        [InlineKeyboardButton("📊 Summary Tally", callback_data="admin_view_summary")],
        [InlineKeyboardButton("👤 Individual Orders", callback_data="admin_view_indiv")],
        [InlineKeyboardButton("💬 View Feedbacks", callback_data="admin_view_feed")],
        [InlineKeyboardButton("📢 Broadcast Message", callback_data="admin_broadcast")],
        [InlineKeyboardButton("✅ Mark ALL Arrived", callback_data="admin_all_arrived")]
    ]
    await update.message.reply_text("<b>🛠 ADMIN CONTROL PANEL</b>", reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)

async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "admin_view_summary":
        conn = sqlite3.connect('food_bot.db')
        inventory = conn.execute("SELECT item, SUM(qty) FROM orders WHERE status='Pending' GROUP BY item").fetchall()
        conn.close()
        msg = "<b>📦 TOTAL ITEMS TO PREPARE:</b>\n\n"
        if not inventory: msg += "No pending items."
        else:
            for item, count in inventory: msg += f"• {item}: <b>{count}</b>\n"
        await query.edit_message_text(msg, parse_mode=ParseMode.HTML)

    elif query.data == "admin_view_indiv":
        conn = sqlite3.connect('food_bot.db')
        details = conn.execute("SELECT users.full_name, item, qty FROM orders JOIN users ON orders.user_id = users.user_id WHERE status='Pending'").fetchall()
        conn.close()
        msg = "<b>👤 INDIVIDUAL PENDING ORDERS:</b>\n\n"
        if not details: msg += "No pending orders."
        else:
            for name, item, qty in details: msg += f"👤 <b>{name}</b>: {qty}x {item}\n"
        await query.edit_message_text(msg, parse_mode=ParseMode.HTML)

    elif query.data == "admin_view_feed":
        conn = sqlite3.connect('food_bot.db')
        feeds = conn.execute("SELECT name, msg FROM feedback ORDER BY id DESC LIMIT 15").fetchall()
        conn.close()
        msg = "<b>💬 USER FEEDBACKS:</b>\n\n"
        if not feeds: msg += "No feedback found."
        else:
            for name, feed in feeds: msg += f"👤 <b>{name}</b>: <i>{feed}</i>\n---\n"
        await query.edit_message_text(msg, parse_mode=ParseMode.HTML)

    elif query.data == "admin_broadcast":
        await query.edit_message_text("🎤 <b>Type your broadcast message:</b>\n(Every user will receive this)", parse_mode=ParseMode.HTML)
        return BROADCAST_TEXT

    elif query.data == "admin_all_arrived":
        conn = sqlite3.connect('food_bot.db')
        users = conn.execute("SELECT DISTINCT user_id FROM orders WHERE status='Pending'").fetchall()
        conn.execute("UPDATE orders SET status='Arrived' WHERE status='Pending'")
        conn.commit()
        conn.close()
        for (uid,) in users:
            try: await context.bot.send_message(uid, "🎁 <b>Your order has arrived! Come and get it!</b> 🏃‍♂️💨", parse_mode=ParseMode.HTML)
            except: pass
        await query.edit_message_text("✅ Everyone has been notified!")
    return ConversationHandler.END

async def perform_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    conn = sqlite3.connect('food_bot.db')
    users = conn.execute("SELECT user_id FROM users").fetchall()
    conn.close()
    
    count = 0
    for (uid,) in users:
        try:
            await context.bot.send_message(uid, f"📢 <b>ANNOUNCEMENT</b>\n\n{msg}", parse_mode=ParseMode.HTML)
            count += 1
        except: continue
    
    await update.message.reply_text(f"✅ Broadcast sent to <b>{count}</b> users.", parse_mode=ParseMode.HTML, reply_markup=get_main_keyboard(ADMIN_ID))
    return ConversationHandler.END

# --- MAIN ---
def main():
    init_db()
    # Fixed Application build with timeouts
    app = Application.builder().token(TOKEN).connect_timeout(30).read_timeout(30).build()
    
    conv = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            MessageHandler(filters.Regex("^🍽 Menu$"), show_menu),
            MessageHandler(filters.Regex("^⚙️ Admin Panel$"), admin_panel),
            MessageHandler(filters.Regex("^💬 Feedback$"), start_feedback),
            MessageHandler(filters.Regex("^👤 Profile$"), start),
            MessageHandler(filters.Regex("^🧾 My Orders$"), view_my_orders),
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
    
    print("Bot is active and running...")
    app.run_polling()

if __name__ == '__main__':
    main()
