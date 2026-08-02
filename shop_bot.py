"""
shop_bot.py — Telegram Shop/Order Bot
Run on Railway: set SHOP_BOT_TOKEN + SHOP_ADMIN_ID env vars.
NOTE: python-telegram-bot v20 manages its own event loop, so we call
app.run_polling() directly (do NOT wrap in asyncio.run).
"""
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("SHOP_BOT_TOKEN", "PASTE_YOUR_BOT_TOKEN_HERE")
ADMIN_ID = int(os.getenv("SHOP_ADMIN_ID", "7411298800"))

MENU = {
    "Burger": 120,
    "Pizza": 250,
    "Cold Coffee": 90,
    "Fries": 80,
}

cart = {}

def menu_kb():
    kb = [[InlineKeyboardButton(f"{k} ₹{v}", callback_data=f"add:{k}")] for k, v in MENU.items()]
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
        item = data.split(":", 1)[1]
        cart.setdefault(uid, {})[item] = cart.get(uid, {}).get(item, 0) + 1
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
    total = sum(MENU[i] * q for i, q in items.items())
    names = ", ".join(f"{i} x{q}" for i, q in items.items())
    ctx.user_data["await_phone"] = False
    cart[uid] = {}
    await update.message.reply_text(f"✅ Order placed! Total ₹{total}. Shop will contact you.")
    if ADMIN_ID:
        try:
            await ctx.bot.send_message(ADMIN_ID, f"🛒 NEW ORDER ₹{total}\n{names}\nCustomer: {txt}")
        except Exception as e:
            print("notify failed:", e)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text))
    print("Bot starting (polling)...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
