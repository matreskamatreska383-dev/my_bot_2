import asyncio
import random
import logging
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import BotCommand, BotCommandScopeDefault, ReplyKeyboardRemove

# --- [ НАСТРОЙКИ ] ---
TOKEN = "8629311774:AAFg-a3tCTFfgVTU4a9HNIX8l3xQHMejLs4"
OWNER_ID = 8330448891 

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- [ БАЗА ДАННЫХ ] ---
users = {}
global_settings = {"tax": 5, "jackpot": 1000000}

CARS = {"Lada": 150000, "BMW M5": 1200000, "Ferrari": 5000000, "Bugatti": 15000000}
HOUSES = {"Трейлер": 50000, "Квартира": 500000, "Вилла": 10000000, "Замок": 100000000}
SHOP = {"Хлеб": 100, "Энергетик": 500, "Аптечка": 2000}

def get_u(m: types.Message):
    uid = m.from_user.id
    if uid not in users:
        users[uid] = {
            "name": m.from_user.full_name, "balance": 25000, "bank": 0, 
            "exp": 0, "lvl": 1, "energy": 100, "health": 100,
            "status": "Игрок", "cars": [], "houses": [], "last_work": datetime.min
        }
    return users[uid]

# --- [ МЕНЮ ] ---
async def set_main_menu(bot: Bot):
    cmds = [
        BotCommand(command="start", description="🖥 Главное меню"),
        BotCommand(command="profile", description="👤 Профиль"),
        BotCommand(command="work", description="⚒ Работа"),
        BotCommand(command="shop", description="🛒 Магазин"),
        BotCommand(command="casino", description="🎰 Казино"),
        BotCommand(command="top", description="🏆 Рейтинг"),
        BotCommand(command="ahelp", description="🛡 Админ-панель")
    ]
    await bot.set_my_commands(cmds, scope=BotCommandScopeDefault())

# --- [ ОСНОВНЫЕ КОМАНДЫ ] ---

@dp.message(Command("start"))
async def start_cmd(m: types.Message):
    get_u(m)
    await m.answer("🏙 **Симулятор живет 24/7!**\nИспользуй меню или команды с точкой (напр. `.профиль`)", parse_mode="Markdown")

@dp.message(F.text.lower().startswith((".профиль", "/profile")))
async def profile_cmd(m: types.Message):
    u = get_u(m)
    text = (
        f"👤 **ИГРОК: {u['name']}**\n"
        f"🎭 Статус: `{u['status']}`\n"
        f"🏅 Уровень: `{u['lvl']}` | ❤️ ХП: `{u['health']}%`\n"
        f"💰 Наличка: `{u['balance']:,}`\n"
        f"🏦 В банке: `{u['bank']:,}`\n"
        f"🚗 Машин: {len(u['cars'])} | 🏠 Домов: {len(u['houses'])}"
    )
    await m.answer(text, parse_mode="Markdown")

@dp.message(F.text.lower().startswith((".работа", "/work")))
async def work_cmd(m: types.Message):
    u = get_u(m)
    if (datetime.now() - u["last_work"]) < timedelta(minutes=5):
        return await m.answer("⏳ Рано! Отдохни 5 минут.")
    pay = random.randint(3000, 9000)
    u["balance"] += pay
    u["last_work"] = datetime.now()
    await m.answer(f"⚒ Ты поработал и получил **{pay:,} 💰**")

# --- [ СИСТЕМА БАНКА ] ---
@dp.message(F.text.lower().startswith(".банк"))
async def bank_put(m: types.Message):
    u = get_u(m)
    try:
        summa = int(m.text.split()[1])
        if u["balance"] >= summa > 0:
            u["balance"] -= summa; u["bank"] += summa
            await m.answer(f"🏦 Внесено: `{summa:,}` 💰")
        else: await m.answer("❌ Недостаточно средств!")
    except: await m.answer("❓ Пример: `.банк 1000`")

@dp.message(F.text.lower().startswith(".снять"))
async def bank_get(m: types.Message):
    u = get_u(m)
    try:
        summa = int(m.text.split()[1])
        if u["bank"] >= summa > 0:
            u["bank"] -= summa; u["balance"] += summa
            await m.answer(f"🏦 Снято: `{summa:,}` 💰")
        else: await m.answer("❌ В банке нет столько денег!")
    except: await m.answer("❓ Пример: `.снять 1000`")

# --- [ ЭКОНОМИКА ] ---
@dp.message(F.text.lower().startswith(".передать"))
async def transfer_cmd(m: types.Message):
    u_from = get_u(m)
    if not m.reply_to_message: return await m.answer("❌ Ответь на сообщение игрока!")
    try:
        summa = int(m.text.split()[-1])
        u_to = get_u(m.reply_to_message)
        if u_from["balance"] >= summa > 0:
            u_from["balance"] -= summa; u_to["balance"] += summa
            await m.answer(f"✅ Передано `{summa:,}` 💰")
    except: await m.answer("❓ `.передать 500` (ответ на смс)")

@dp.message(F.text.lower() == ".топ")
async def top_cmd(m: types.Message):
    top = sorted(users.items(), key=lambda x: x[1]['balance'], reverse=True)[:10]
    res = "🏆 **TOP 10 БОГАЧЕЙ:**\n"
    for i, (uid, d) in enumerate(top, 1):
        res += f"{i}. {d['name']} — `{d['balance']:,}` 💰\n"
    await m.answer(res)

# --- [ АДМИН-КОМАНДЫ (ДЛЯ ТЕБЯ) ] ---

@dp.message(Command("ahelp"))
async def admin_help(m: types.Message):
    if m.from_user.id != OWNER_ID: return
    text = (
        "👑 **ПАНЕЛЬ ОСНОВАТЕЛЯ:**\n"
        "├ `.выдать [сумма]` — выдать денег (ответ на смс)\n"
        "├ `.уб [сумма]` — установить баланс (ответ на смс)\n"
        "├ `.выдатьстатус [название]` — (ответ на смс)\n"
        "└ `/рассылка [текст]` — сообщение всем"
    )
    await m.answer(text)

@dp.message(F.text.lower().startswith(".выдатьстатус"))
async def adm_status(m: types.Message):
    if m.from_user.id != OWNER_ID or not m.reply_to_message: return
    status = m.text.split(maxsplit=1)[1]
    target = get_u(m.reply_to_message)
    target["status"] = status
    await m.answer(f"✅ Игроку {target['name']} выдан статус: **{status}**")

@dp.message(F.text.lower().startswith(".уб"))
async def adm_set_bal(m: types.Message):
    if m.from_user.id != OWNER_ID or not m.reply_to_message: return
    val = int(m.text.split()[-1])
    target = get_u(m.reply_to_message)
    target["balance"] = val
    await m.answer(f"✅ Баланс {target['name']} изменен на `{val:,}`")

@dp.message(F.text.lower().startswith(".выдать"))
async def adm_give_bal(m: types.Message):
    if m.from_user.id != OWNER_ID or not m.reply_to_message: return
    val = int(m.text.split()[-1])
    target = get_u(m.reply_to_message)
    target["balance"] += val
    await m.answer(f"✅ Выдано `{val:,}` 💰 игроку {target['name']}")

# --- [ ЗАПУСК ] ---
async def main():
    await set_main_menu(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
