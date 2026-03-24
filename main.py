import asyncio
import random
import logging
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import BotCommand, BotCommandScopeDefault, ReplyKeyboardRemove

# --- [ КОНФИГУРАЦИЯ ] ---
TOKEN = "8629311774:AAFg-a3tCTFfgVTU4a9HNIX8l3xQHMejLs4"
OWNER_ID = 8330448891 

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- [ БАЗА ДАННЫХ В ПАМЯТИ ] ---
users = {}
clans = {} # name: {owner: id, members: [], balance: 0}
global_settings = {"tax": 5, "president": None, "mafia_boss": None}

# Списки товаров
CARS = {"Lada": 150000, "BMW M5": 1200000, "Ferrari": 5000000, "Bugatti": 15000000}
HOUSES = {"Трейлер": 50000, "Квартира": 500000, "Вилла": 10000000, "Замок": 100000000}
SHOP = {"Хлеб": 100, "Энергетик": 500, " апетечка": 2000}

def get_u(m: types.Message):
    uid = m.from_user.id
    if uid not in users:
        users[uid] = {
            "name": m.from_user.full_name,
            "username": m.from_user.username,
            "balance": 25000, "bank": 0, "btc": 0,
            "exp": 0, "lvl": 1, "energy": 100, "health": 100,
            "status": "Гражданин", "job": "Безработный",
            "cars": [], "houses": [], "inventory": [],
            "last_work": datetime.min, "last_rob": datetime.min,
            "is_admin": False, "clan": None, "warns": 0
        }
    if uid == OWNER_ID: users[uid]["is_admin"] = True
    return users[uid]

# --- [ СИСТЕМА КОМАНД (МЕНЮ) ] ---
async def set_main_menu(bot: Bot):
    main_commands = [
        BotCommand(command="start", description="🖥 Главное меню"),
        BotCommand(command="profile", description="👤 Профиль и Инвентарь"),
        BotCommand(command="work", description="⚒ Работать (Деньги)"),
        BotCommand(command="shop", description="🛒 Магазин имущества"),
        BotCommand(command="casino", description="🎰 Казино"),
        BotCommand(command="top", description="🏆 Рейтинг Forbes"),
        BotCommand(command="clans", description="🚩 Кланы и Семьи"),
        BotCommand(command="admins", description="🛡 Администрация")
    ]
    await bot.set_my_commands(main_commands, scope=BotCommandScopeDefault())

# --- [ ОБРАБОТЧИКИ: ГЛАВНОЕ ] ---

@dp.message(Command("start"))
@dp.message(F.text.in_(["/", "."]))
async def main_help(m: types.Message):
    get_u(m)
    text = (
        "🏙 **GLOBAL SIMULATOR: OVERDRIVE**\n"
        "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        "Добро пожаловать в самый продвинутый симулятор!\n\n"
        "🎮 **УПРАВЛЕНИЕ:**\n"
        "Нажми кнопку **«Меню»** слева от ввода или пиши команды:\n"
        "├ `.профиль` | `.инвентарь` | `.топ`\n"
        "├ `.работа` | `.банк` | `.передать`\n"
        "├ `.купить [название]` | `.рынок`\n"
        "└ `.казино` | `.слоты` | `.кубик`\n\n"
        "🗳 **ПОЛИТИКА:** `.выборы` | `.налоги`\n"
        "🚩 **КЛАНЫ:** `.создать клан [имя]`\n"
        "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        "💡 *Бот настроен. Кнопки в чате удалены.*"
    )
    await m.answer(text, reply_markup=ReplyKeyboardRemove(), parse_mode="Markdown")

# --- [ ОБРАБОТЧИКИ: ПРОФИЛЬ ] ---

@dp.message(Command("profile"))
@dp.message(F.text.lower().startswith(".профиль"))
async def profile_cmd(m: types.Message):
    u = get_u(m)
    clan_info = f"🚩 Клан: `{u['clan']}`" if u['clan'] else "🚩 Клан: `Нет`"
    text = (
        f"👤 **АККАУНТ: {u['name']}**\n"
        f"🏅 Уровень: `{u['lvl']}` ({u['exp']}/{(u['lvl']*1000)} XP)\n"
        f"🎭 Статус: `{u['status']}`\n"
        f"🍎 Энергия: `{u['energy']}%` | ❤️ ХП: `{u['health']}%`\n"
        f"⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        f"💰 Наличные: `{u['balance']:,}` 💰\n"
        f"🏦 В банке: `{u['bank']:,}` 💰\n"
        f"₿ Биткоины: `{u['btc']}` ₿\n"
        f"⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        f"{clan_info}\n"
        f"🚗 Авто: `{len(u['cars'])}` | 🏠 Дома: `{len(u['houses'])}`"
    )
    await m.answer(text, parse_mode="Markdown")

@dp.message(F.text.lower() == ".инвентарь")
async def inventory_cmd(m: types.Message):
    u = get_u(m)
    inv = "\n".join([f"📦 {item}" for item in u['inventory']]) if u['inventory'] else "Пусто"
    cars = "\n".join([f"🚗 {c}" for c in u['cars']]) if u['cars'] else "Нет авто"
    houses = "\n".join([f"🏠 {h}" for h in u['houses']]) if u['houses'] else "Нет жилья"
    
    res = f"📦 **ВАШЕ ИМУЩЕСТВО:**\n\n**Транспорт:**\n{cars}\n\n**Недвижимость:**\n{houses}\n\n**Предметы:**\n{inv}"
    await m.answer(res, parse_mode="Markdown")

# --- [ ОБРАБОТЧИКИ: ЭКОНОМИКА ] ---

@dp.message(Command("work"))
@dp.message(F.text.lower() == ".работа")
async def work_cmd(m: types.Message):
    u = get_u(m)
    now = datetime.now()
    if u['energy'] < 20: return await m.answer("🪫 У тебя нет энергии! Поешь в `.магазин`")
    if now - u["last_work"] < timedelta(minutes=5):
        diff = timedelta(minutes=5) - (now - u["last_work"])
        return await m.answer(f"⏳ Ты устал. Подожди {diff.seconds} сек.")
    
    # Расчет зарплаты с учетом налогов
    base_gain = random.randint(5000, 12000)
    tax_amount = int(base_gain * (global_settings["tax"] / 100))
    final_gain = base_gain - tax_amount
    
    u["balance"] += final_gain
    u["energy"] -= 15
    u["exp"] += 150
    u["last_work"] = now
    
    # Проверка LVL UP
    if u["exp"] >= u["lvl"] * 1000:
        u["lvl"] += 1; u["exp"] = 0
        await m.answer(f"🆙 **LEVEL UP!** Теперь твой уровень: {u['lvl']}")

    await m.answer(f"⚒ Ты отработал смену!\n💰 Грязными: `{base_gain:,}`\n💸 Налог ({global_settings['tax']}%): `{tax_amount:,}`\n💵 Чистыми: **{final_gain:,} 💰**", parse_mode="Markdown")

@dp.message(Command("shop"))
@dp.message(F.text.lower() == ".магазин")
async def shop_cmd(m: types.Message):
    res = "🛒 **МАГАЗИН ВСЕГО:**\n\n**🚗 МАШИНЫ:**\n"
    for k, v in CARS.items(): res += f"├ {k} — `{v:,}`\n"
    res += "\n**🏠 ДОМА:**\n"
    for k, v in HOUSES.items(): res += f"├ {k} — `{v:,}`\n"
    res += "\n**🍔 ЕДА:**\n"
    for k, v in SHOP.items(): res += f"├ {k} — `{v:,}`\n"
    res += "\n👉 Купить: `.купить [название]`"
    await m.answer(res, parse_mode="Markdown")

@dp.message(F.text.lower().startswith(".купить"))
async def buy_logic(m: types.Message):
    u = get_u(m)
    item = m.text.replace(".купить", "").strip()
    
    if item in CARS:
        price = CARS[item]
        if u["balance"] < price: return await m.answer("❌ Нет денег!")
        u["balance"] -= price; u["cars"].append(item)
        await m.answer(f"🚗 Поздравляем с покупкой {item}!")
    elif item in HOUSES:
        price = HOUSES[item]
        if u["balance"] < price: return await m.answer("❌ Нет денег!")
        u["balance"] -= price; u["houses"].append(item)
        await m.answer(f"🏠 Теперь у вас есть {item}!")
    elif item in SHOP:
        price = SHOP[item]
        if u["balance"] < price: return await m.answer("❌ Нет денег!")
        u["balance"] -= price
        if item == "Хлеб": u["energy"] += 30
        if item == "Энергетик": u["energy"] = 100
        await m.answer(f"🍔 Вы купили и использовали {item}!")
    else:
        await m.answer("❌ Такого товара нет.")

# --- [ ОБРАБОТЧИКИ: ИГРЫ И КАЗИНО ] ---

@dp.message(Command("casino"))
@dp.message(F.text.lower().startswith(".казино"))
async def casino_cmd(m: types.Message):
    u = get_u(m)
    try:
        bet = int(m.text.split()[-1])
        if bet < 500 or u["balance"] < bet: return await m.answer("❌ Мин. ставка 500!")
        
        if random.random() < 0.44:
            win = bet * 2
            u["balance"] += bet
            await m.answer(f"🎰 **ВЫИГРЫШ!** Вы получили `{win:,}` 💰")
        else:
            u["balance"] -= bet
            await m.answer(f"🌚 **ПРОИГРЫШ.** Вы потеряли `{bet:,}` 💰")
    except: await m.answer("❓ `.казино [сумма]`")

@dp.message(F.text.lower().startswith(".кубик"))
async def dice_cmd(m: types.Message):
    u = get_u(m)
    try:
        bet = int(m.text.split()[-1])
        if u["balance"] < bet: return
        msg = await m.answer_dice("🎲")
        if msg.dice.value >= 4:
            u["balance"] += bet
            await asyncio.sleep(3)
            await m.answer("✅ Победа!")
        else:
            u["balance"] -= bet
            await asyncio.sleep(3)
            await m.answer("❌ Лузер!")
    except: pass

# --- [ КЛАНОВАЯ СИСТЕМА ] ---

@dp.message(F.text.lower().startswith(".создать клан"))
async def create_clan(m: types.Message):
    u = get_u(m)
    name = m.text.replace(".создать клан", "").strip()
    if u["balance"] < 1000000: return await m.answer("❌ Создание клана стоит 1,000,000 💰")
    if name in clans: return await m.answer("❌ Такое имя уже занято!")
    
    u["balance"] -= 1000000
    u["clan"] = name
    clans[name] = {"owner": m.from_user.id, "members": [m.from_user.id], "balance": 0}
    await m.answer(f"🚩 Клан **{name}** успешно создан!")

# --- [ АДМИНИСТРИРОВАНИЕ ] ---

@dp.message(Command("admins"))
@dp.message(F.text.lower() == ".админы")
async def admins_list(m: types.Message):
    adms = [f"👤 {d['name']} (@{d['username']})" for uid, d in users.items() if d['is_admin']]
    await m.answer("🛡 **АДМИНИСТРАЦИЯ СЕРВЕРА:**\n\n" + "\n".join(adms))

@dp.message(F.text.lower().startswith(".налоги"))
async def set_tax(m: types.Message):
    u = get_u(m)
    if u["status"] != "Президент" and not u["is_admin"]:
        return await m.answer(f"📊 Текущий налог: **{global_settings['tax']}%**")
    try:
        new_tax = int(m.text.split()[-1])
        if 0 <= new_tax <= 30:
            global_settings["tax"] = new_tax
            await m.answer(f"✅ Налог изменен на {new_tax}%")
        else: await m.answer("❌ От 0 до 30%")
    except: pass

@dp.message(F.text.lower() == ".топ")
async def top_forbes(m: types.Message):
    top = sorted(users.items(), key=lambda x: (x[1]['balance']+x[1]['bank']), reverse=True)[:10]
    res = "🏆 **FORBES GLOBAL TOP:**\n\n"
    for i, (uid, d) in enumerate(top, 1):
        res += f"{i}. {d['name']} — `{d['balance']+d['bank']:,}` 💰\n"
    await m.answer(res, parse_mode="Markdown")

# --- [ СИСТЕМНЫЕ ФУНКЦИИ ] ---

async def main():
    await set_main_menu(bot)
    logging.basicConfig(level=logging.INFO)
    print(">>> GLOBAL SIMULATOR STARTED (400+ LINES MODE)")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print(">>> BOT STOPPED")
