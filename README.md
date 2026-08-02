# Telegram Shop Bot

Production-ready Telegram order bot for local businesses (restaurants, salons, kirana shops). Customers tap a menu, place an order, and the shop owner gets notified instantly.

## Features
- Inline menu with prices (edit per client)
- Add-to-cart + quantity tracking
- Customer name + phone capture
- SQLite order storage
- Owner gets notified on every new order (via Telegram)
- Built on python-telegram-bot

## Setup
1. Create a bot via @BotFather and copy the token.
2. Set env vars:
   ```
   export SHOP_BOT_TOKEN="your_bot_token"
   export SHOP_ADMIN_ID="your_telegram_user_id"
   ```
3. Install deps:
   ```
   pip install python-telegram-bot==20.7
   ```
4. Run:
   ```
   python3 shop_bot.py
   ```

## Customize
- Edit the `MENU` dict in `shop_bot.py` for the client's products/prices.
- Orders are saved in `shop_orders.db`.

## License
MIT — free to use, modify, and sell.
