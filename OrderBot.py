import os
import sqlite3
import logging
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    CallbackQueryHandler, filters, ContextTypes, ConversationHandler
)

# Load environment variables
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# States
(REGISTRATION, MENU_SELECTION, QTY_INPUT, ADD_MORE_PROMPT, 
 CONFIRM_ORDER, BROADCAST_TEXT, GIVING_FEEDBACK, 
 EDIT_MENU_PRICE, ADD_ITEM_NAME, ADD_ITEM_PRICE) = range(10)

# --- DATABASE LOGIC ---
def init_db():
    conn = sqlite3.connect('food_bot.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, full_name TEXT, username TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, item TEXT, qty INTEGER, status TEXT, timestamp DATETIME)')
    c.execute('CREATE TABLE IF NOT EXISTS feedback (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, name TEXT, msg TEXT)')
    # New Table for Dynamic Menu
    c.execute('CREATE TABLE IF NOT EXISTS menu (name TEXT PRIMARY KEY, price REAL)')
    
    # Seed initial menu if empty
    c.execute("SELECT COUNT(*) FROM menu")
    if c.fetchone()[0] == 0:
        initial_menu = [("🍔 Burger", 5.0), ("🍕 Pizza", 8.0), ("🍟 Fries", 2.5), ("🥤 Coke", 1.5)]
        c.executemany("INSERT INTO menu VALUES (?, ?)", initial_menu)
    
    conn.commit()
    conn.close()

def get_menu():
    conn = sqlite3.connect('food_bot.db')
    menu = {row[0]: row[1] for row in conn.execute("SELECT name, price FROM menu").fetchall()}
    conn.close()
    return menu

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
        await update.message.reply_text("👋 Welcome! Please enter your <b>Full Name</b> to register:", parse_mode=ParseMode.HTML)
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
    await update.message.reply_text("✅ Registered!", reply_markup=get_main_keyboard(user_id))
    return ConversationHandler.END

# --- ORDERING SYSTEM (Dynamic) ---
async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_menu = get_menu()
    context.user_data['session_items'] = []
    kb = [[InlineKeyboardButton(f"{k} - ${v}", callback_data=f"order_{k}")] for k, v in current_menu.items()]
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
    
    current_menu = get_menu()
    item = context.user_data['current_item']
    context.user_data['session_items'].append({'item': item, 'qty': int(qty), 'price': current_menu[item]})
    total = sum(i['qty'] * i['price'] for i in context.user_data['session_items'])
    
    kb = [[InlineKeyboardButton("➕ Add More", callback_data="add_more")],
          [InlineKeyboardButton(f"✅ Review Order (${total:.2f})", callback_data="review")]]
    await update.message.reply_text(f"Added {qty}x {item}.", reply_markup=InlineKeyboardMarkup(kb))
    return ADD_MORE_PROMPT

async def review_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "add_more":
        current_menu = get_menu()
        kb = [[InlineKeyboardButton(f"{k}", callback_data=f"order_{k}")] for k in current_menu.keys()]
        await query.edit_message_text("Select another item:", reply_markup=InlineKeyboardMarkup(kb))
        return MENU_SELECTION
    
    total = sum(i['qty'] * i['price'] for i in context.user_data['session_items'])
    summary = "<b>🛒 FINAL ORDER REVIEW</b>\n\n"
    for i in context.user_data['session_items']:
        summary += f"• {i['qty']}x {i['item']} - <i>${i['qty']*i['price']:.2f}</i>\n"
    summary += f"\n<b>💰 TOTAL: ${total:.2f}</b>\n\nConfirm order?"
    
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
    
    admin_summary = f"🔔 <b>NEW ORDER FROM: {user_name}</b>\n\n"
    total_cost = 0
    for i in context.user_data['session_items']:
        cost = i['qty'] * i['price']
        total_cost += cost
        admin_summary += f"• {i['qty']}x {i['item']} (<i>${cost:.2f}</i>)\n"
        conn.execute("INSERT INTO orders (user_id, item, qty, status, timestamp) VALUES (?, ?, ?, ?, ?)",
                     (user_id, i['item'], i['qty'], "Pending", datetime.now()))
    admin_summary += f"\n💰 <b>TOTAL: ${total_cost:.2f}</b>"
    conn.commit()
    conn.close()

    await query.edit_message_text(f"✅ <b>Order Placed!</b>\nTotal: ${total_cost:.2f}", parse_mode=ParseMode.HTML)
    await context.bot.send_message(chat_id=ADMIN_ID, text=admin_summary, parse_mode=ParseMode.HTML)
    return ConversationHandler.END

# --- ADMIN: EDIT MENU FEATURE ---
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    kb = [
        [InlineKeyboardButton("📊 Summary Tally", callback_data="admin_view_summary")],
        [InlineKeyboardButton("👤 Individual Orders", callback_data="admin_view_indiv")],
        [InlineKeyboardButton("✏️ Edit Menu", callback_data="admin_edit_menu")],
        [InlineKeyboardButton("📢 Broadcast Message", callback_data="admin_broadcast")],
        [InlineKeyboardButton("✅ Mark ALL Arrived", callback_data="admin_all_arrived")]
    ]
    await update.message.reply_text("<b>🛠 ADMIN PANEL</b>", reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)

async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "admin_edit_menu":
        current_menu = get_menu()
        txt = "<b>Current Menu:</b>\n"
        kb = []
        for name, price in current_menu.items():
            txt += f"• {name}: ${price}\n"
            kb.append([InlineKeyboardButton(f"❌ Delete {name}", callback_data=f"del_{name}")])
        kb.append([InlineKeyboardButton("➕ Add New Item", callback_data="add_new_item")])
        await query.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)

    elif query.data == "add_new_item":
        await query.edit_message_text("Type the NAME of the new food/drink:")
        return ADD_ITEM_NAME

    elif query.data.startswith("del_"):
        item_to_del = query.data.replace("del_", "")
        conn = sqlite3.connect('food_bot.db')
        conn.execute("DELETE FROM menu WHERE name=?", (item_to_del,))
        conn.commit()
        conn.close()
        await query.edit_message_text(f"🗑 Deleted {item_to_del} from menu.")
        return ConversationHandler.END

    elif query.data == "admin_broadcast":
        await query.edit_message_text("🎤 <b>Type your broadcast message:</b>", parse_mode=ParseMode.HTML)
        return BROADCAST_TEXT

    elif query.data == "admin_view_summary":
        conn = sqlite3.connect('food_bot.db')
        inventory = conn.execute("SELECT item, SUM(qty) FROM orders WHERE status='Pending' GROUP BY item").fetchall()
        conn.close()
        msg = "<b>📦 TOTAL ITEMS TO PREPARE:</b>\n\n"
        for item, count in inventory: msg += f"• {item}: <b>{count}</b>\n"
        await query.edit_message_text(msg or "No pending items.", parse_mode=ParseMode.HTML)

    elif query.data == "admin_view_indiv":
        conn = sqlite3.connect('food_bot.db')
        details = conn.execute("SELECT orders.id, users.full_name, item, qty FROM orders JOIN users ON orders.user_id = users.user_id WHERE status='Pending'").fetchall()
        conn.close()
        if not details:
            await query.edit_message_text("No pending orders.")
            return
        await query.edit_message_text("<b>👤 PENDING ORDERS:</b>", parse_mode=ParseMode.HTML)
        for oid, name, item, qty in details:
            kb = [[InlineKeyboardButton(f"✅ Delivered", callback_data=f"indiv_arrived_{oid}")]]
            await context.bot.send_message(ADMIN_ID, f"👤 <b>{name}</b>\n{qty}x {item}", reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)

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

# --- ADMIN MENU EDIT FLOW ---
async def add_item_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['new_item_name'] = update.message.text
    await update.message.reply_text(f"What is the price for {update.message.text}? (e.g., 5.50)")
    return ADD_ITEM_PRICE

async def add_item_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price_text = update.message.text
    try:
        price = float(price_text)
        name = context.user_data['new_item_name']
        conn = sqlite3.connect('food_bot.db')
        conn.execute("INSERT INTO menu (name, price) VALUES (?, ?)", (name, price))
        conn.commit()
        conn.close()
        await update.message.reply_text(f"✅ Added {name} at ${price:.2f} to the menu!", reply_markup=get_main_keyboard(ADMIN_ID))
    except:
        await update.message.reply_text("❌ Invalid price. Item not added. Use /start to try again.")
    return ConversationHandler.END

# --- BROADCAST & MISC ---
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
    await update.message.reply_text(f"✅ Broadcast sent to <b>{count}</b> users.", reply_markup=get_main_keyboard(ADMIN_ID), parse_mode=ParseMode.HTML)
    return ConversationHandler.END

async def indiv_mark_arrived(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    oid = query.data.replace("indiv_arrived_", "")
    conn = sqlite3.connect('food_bot.db')
    order_data = conn.execute("SELECT user_id, item, qty FROM orders WHERE id=?", (oid,)).fetchone()
    if order_data:
        uid, item, qty = order_data
        conn.execute("UPDATE orders SET status='Arrived' WHERE id=?", (oid,))
        conn.commit()
        try: await context.bot.send_message(uid, f"✅ <b>Order Arrived!</b>\nYour <b>{qty}x {item}</b> is ready! 🏃‍♂️", parse_mode=ParseMode.HTML)
        except: pass
        await query.edit_message_text(f"✅ Delivered: {qty}x {item}.")
    conn.close()

async def view_my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conn = sqlite3.connect('food_bot.db')
    orders = conn.execute("SELECT item, qty, status FROM orders WHERE user_id=? ORDER BY timestamp DESC LIMIT 5", (user_id,)).fetchall()
    conn.close()
    if not orders:
        await update.message.reply_text("❌ No orders yet.")
        return
    msg = "<b>🧾 RECENT ORDERS</b>\n\n"
    for item, qty, status in orders:
        msg += f"• <b>{item}</b> (x{qty}) - {status}\n"
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

async def start_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📝 Type your feedback:")
    return GIVING_FEEDBACK

async def save_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    msg = update.message.text
    conn = sqlite3.connect('food_bot.db')
    name = conn.execute("SELECT full_name FROM users WHERE user_id=?", (user_id,)).fetchone()[0]
    conn.execute("INSERT INTO feedback (user_id, name, msg) VALUES (?, ?, ?)", (user_id, name, msg))
    conn.commit()
    conn.close()
    await update.message.reply_text("❤️ Thanks!", reply_markup=get_main_keyboard(user_id))
    return ConversationHandler.END

# --- MAIN ---
def main():
    init_db()
    app = Application.builder().token(TOKEN).connect_timeout(30).read_timeout(30).build()
    
    conv = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            MessageHandler(filters.Regex("^🍽 Menu$"), show_menu),
            MessageHandler(filters.Regex("^⚙️ Admin Panel$"), admin_panel),
            MessageHandler(filters.Regex("^💬 Feedback$"), start_feedback),
            MessageHandler(filters.Regex("^🧾 My Orders$"), view_my_orders),
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
            ADD_ITEM_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_item_name)],
            ADD_ITEM_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_item_price)],
        },
        fallbacks=[CommandHandler('start', start)],
    )

    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(admin_callback, pattern="^admin_"))
    app.add_handler(CallbackQueryHandler(indiv_mark_arrived, pattern="^indiv_arrived_"))
    app.run_polling()

if __name__ == '__main__':
    main()
