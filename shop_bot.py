"""
shop_bot.py — Telegram Shop/Order Bot for local businesses
Sell this to restaurants, salons, kirana shops at ₹15-30k each.
Run: pip install python-telegram-bot==20.7; python3 shop_bot.py
Config: set BOT_TOKEN and ADMIN_ID below (or use env vars).
"""
import os
import sqlite3
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("SHOP_BOT_TOKEN", "PASTE_YOUR_BOT_TOKEN_HERE")
ADMIN_ID = int(os.getenv("SHOP_ADMIN_ID", "0"))  # your telegram user id

# ---- menu (edit per client) ----
MENU = {
    "Burger": 120,
    "Pizza": 250,
    "Cold Coffee": 90,
    "Fries": 80,
}

# ---- db ----
conn = sqlite3.connect("shop_orders.db", check_same_thread=False)
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cust_name TEXT, item TEXT, qty INT, total INT,
    phone TEXT, status TEXT, ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
conn.commit()

cart = {}  # user_id -> {item: qty}

def menu_kb():
    kb = [[InlineKeyboardButton(f"{k} ₹{v}", callback_data=f"add:{k}")] for k in MENU]
    kb.append([InlineKeyboardButton("✅ Place Order", callback_data="checkout")])
    kb.append([InlineKeyboardButton("🗑 Clear", callback_data="clear")])
    return InlineKeyboardMarkup(kb)

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    cart[uid] = {}
    await update.message.reply_text(
        "🍔 *Welcome! Tap to add items, then Place Order.*",
        reply_markup=menu_kb(), parse_mode="Markdown")

async def button(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    data = q.data
    if data.startswith("add:"):
        item = data.split(":",1)[1]
        cart.setdefault(uid, {})[item] = cart.get(uid,{}).get(item,0)+1
        await q.edit_message_text(f"Added *{item}* x{cart[uid][item]}\nTap more or Place Order.",
                                   reply_markup=menu_kb(), parse_mode="Markdown")
    elif data == "clear":
        cart[uid] = {}
        await q.edit_message_text("Cart cleared.", reply_markup=menu_kb())
    elif data == "checkout":
        await q.edit_message_text("📞 Send your *NAME and PHONE* to confirm order:", parse_mode="Markdown")
        ctx.user_data["await_phone"] = True

async def text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not ctx.user_data.get("await_phone"):
        return
    txt = update.message.text
    items = cart.get(uid, {})
    if not items:
        await update.message.reply_text("Cart empty, /start again.")
        return
    total = sum(MENU[i]*q for i,q in items.items())
    names = ", ".join(f"{i} x{q}" for i,q in items.items())
    c.execute("INSERT INTO orders (cust_name,item,qty,total,phone,status) VALUES (?,?,?,?,?,?)",
              (txt.split()[0] if txt else "cust", names, sum(items.values()), total, txt, "NEW"))
    conn.commit()
    ctx.user_data["await_phone"] = False
    cart[uid] = {}
    await update.message.reply_text(f"✅ Order placed! Total ₹{total}. Shop will contact you.")
    if ADMIN_ID:
        await ctx.bot.send_message(ADMIN_ID, f"🛒 NEW ORDER ₹{total}\n{names}\nCustomer: {txt}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text))
    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
