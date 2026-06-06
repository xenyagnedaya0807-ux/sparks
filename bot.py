import os
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- ДАННЫЕ В ПАМЯТИ (простая версия без базы данных) ---
users = {}
inventory = {}

# --- ГАЧА ---
gacha_items = {
    "common": ["Листья", "Повязка", "Марля", "Цветы", "Носки"],
    "uncommon": ["Жемчужное ожерелье", "Кулон с клыком", "Платки"],
    "rare": ["Перьевая корона", "Бандана", "Галстук"],
    "epic": ["Корона", "Плащ", "Колчан"],
    "legendary": ["Тиара", "Военное обмундирование", "Накидка"],
    "mythic": ["Маска", "Доспехи"],
    "divine": ["Золотой венец"],
    "mega": ["Питомец"]
}

gacha_prices = {
    30: ["common", "uncommon", "rare", "epic"],
    150: ["common", "uncommon", "rare", "epic", "legendary"],
    300: ["uncommon", "rare", "epic", "legendary", "mythic"],
    600: ["rare", "epic", "legendary", "mythic", "divine", "mega"]
}

# --- УТИЛИТЫ ---
def get_balance(user_id):
    return users.get(user_id, 100)

def change_balance(user_id, amount):
    users[user_id] = get_balance(user_id) + amount

def add_item(user_id, item):
    inventory.setdefault(user_id, []).append(item)

# --- КОМАНДЫ ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ Добро пожаловать в SparksWallet!\n\nКоманды:\n/balance\n/shop\n/roll <30|150|300|600>"
    )

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(f"✨ У тебя {get_balance(user_id)} искр")

async def give(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return
    user_id = int(context.args[0])
    amount = int(context.args[1])
    change_balance(user_id, amount)
    await update.message.reply_text("✔️ Выдано")

async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not context.args:
        await update.message.reply_text("Используй /roll 30|150|300|600")
        return

    cost = int(context.args[0])

    if cost not in gacha_prices:
        await update.message.reply_text("Нет такой гачи")
        return

    if get_balance(user_id) < cost:
        await update.message.reply_text("❌ Недостаточно искр")
        return

    change_balance(user_id, -cost)

    rarity = random.choice(gacha_prices[cost])
    item = random.choice(gacha_items[rarity])

    add_item(user_id, item)

    await update.message.reply_text(
        f"🎲 Крутка за {cost} искр\n"
        f"✨ Редкость: {rarity}\n"
        f"🎁 Выпало: {item}"
    )

async def inventory_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    items = inventory.get(user_id, [])
    if not items:
        await update.message.reply_text("Инвентарь пуст")
    else:
        await update.message.reply_text("📦 Твой инвентарь:\n" + "\n".join(items))

# --- ЗАПУСК ---
def main():
    token = os.getenv("BOT_TOKEN")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("give", give))
    app.add_handler(CommandHandler("roll", roll))
    app.add_handler(CommandHandler("inventory", inventory_cmd))

    app.run_polling()

if __name__ == "__main__":
    main()
