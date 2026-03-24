import asyncio
import random
import logging
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import BotCommand, BotCommandScopeDefault, ReplyKeyboardRemove

# --- [ СИСТЕМНЫЙ БЛОК ] ---
TOKEN = "8629311774:AAFg-a3tCTFfgVTU4a9HNIX8l3xQHMejLs4"
OWNER_ID = 8330448891 

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- [ ГЛОБАЛЬНАЯ ДАТА-БАЗА ] ---
users = {}
banned_users = set()
muted_users = {} # {id: time}
votes = {} # {user_id: candidate_id}

# Динамические курсы
rates = {"btc": 500000, "eth": 35000, "apple": 1500, "google": 2800}

global_state = {
    "tax": 5,
    "president": None,
    "election_open": True,
    "jackpot": 10000000
}

# Списки товаров
CARS = {"Lada": 150000, "BMW": 1200000, "Tesla": 5000000, "Bugatti": 20000000}
HOUSES = {"Трейлер": 50000, "Квартира": 800000, "Вилла": 15000000, "Замок": 100000000}
BUSINESS = {"Киоск": 300000, "СТО": 2000000, "Завод": 50000000}

# --- [ ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ] ---

def get_u(m: types.Message):
    uid = m.from_user.id
    if uid not in users:
        users[uid] = {
            "name": m.from_user.full_name, "user": m.from_user.username or "None",
            "balance": 25000, "bank": 0, "btc": 0, "eth": 0,
            "stocks": {"apple": 0, "google": 0},
            "lvl": 1, "exp": 0, "energy": 100, "hp": 100,
            "status": "Гражданин", "cars": [], "houses": [], "biz": [],
            "last_work": datetime.min, "is_admin": False
        }
    if uid == OWNER_ID: users[uid]["is_admin"] = True
    return users[uid]

async def check_admin(m: types.Message):
    if m.from_user.id == OWNER_ID: return True
    await m.answer("⚠️ Ошибка доступа: Вы не являетесь Основателем!")
    return False

# --- [ ОБРАБОТКА МУТА И БАНА ] ---
@dp.message()
async def middleware(message: types.Message, next_handler):
    uid = message.from_user.id
    if uid in banned_users: return 
    if uid in muted_users:
        if datetime.now() < muted_users[uid]:
            return await message.answer("🤐 Вы не можете писать, у вас мут!")
        else: del muted_users[uid]
    return await next_handler(message)

# --- [ КОМАНДЫ СТАРТА И МЕНЮ ] ---

async def set_main_menu(bot: Bot):
    cmds = [
        BotCommand(command="start", description="🖥 Меню"),
        BotCommand(command="profile", description="👤 Профиль"),
        BotCommand(command="work", description="⚒ Работа"),
        BotCommand(command="shop", description="🛒 Магазин"),
        BotCommand(command="market", description="📈 Биржа"),
        BotCommand(command="casino", description="🎰 Казино"),
        BotCommand(command="top", description="🏆 Forbes"),
        BotCommand(command="vote", description="🗳 Выборы"),
        BotCommand(command="ahelp", description="🛡 Админ-панель")
    ]
    await bot.set_my_commands(cmds, scope=BotCommandScopeDefault())

@dp.message(Command("start"))
async def cmd_start(m: types.Message):
    get_u(m)
    await m.answer(
        "🏙 **GLOBAL SIMULATOR: MONSTER EDITION**\n"
        "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        "Ты в игре! Здесь можно стать Президентом, крипто-магнатом или владельцем заводов.\n\n"
        "🔹 `.профиль` | `.инвентарь` | `.топ`\n"
        "🔹 `.работа` | `.банк` | `.снять`\n"
        "🔹 `.крипта` | `.акции` | `.биржа`\n"
        "🔹 `.казино` | `.слоты` | `.кубик`\n"
        "🔹 `.выборы` | `.голосовать` [ID]\n\n"
        "⚙️ **Управление:** Используй кнопки меню или префикс `.`",
        parse_mode="Markdown"
    )

# --- [ ПРОФИЛЬ И ИНВЕНТАРЬ ] ---

@dp.message(F.text.lower().startswith((".профиль", "/profile")))
async def profile_view(m: types.Message):
    u = get_u(m)
    txt = (
        f"👤 **ДОКУМЕНТЫ: {u['name']}**\n"
        f"🏅 Уровень: `{u['lvl']}` ({u['exp']}/{(u['lvl']*1000)})\n"
        f"🎭 Статус: **{u['status']}**\n"
        f"🍎 Энергия: `{u['energy']}%` | ❤️ ХП: `{u['hp']}%`\n"
        f"⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        f"💰 Наличка: `{u['balance']:,}` 💰\n"
        f"🏦 В банке: `{u['bank']:,}` 💰\n"
        f"₿ BTC: `{u['btc']:.4f}` | Ξ ETH: `{u['eth']:.2f}`\n"
        f"⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        f"🚗 Авто: {len(u['cars'])} | 🏠 Дома: {len(u['houses'])} | 🏢 Бизнес: {len(u['biz'])}"
    )
    await m.answer(txt, parse_mode="Markdown")

@dp.message(F.text.lower() == ".инвентарь")
async def inv_view(m: types.Message):
    u = get_u(m)
    res = "📦 **ТВОИ ВЕЩИ:**\n\n"
    res += "**Машины:** " + (", ".join(u['cars']) if u['cars'] else "Нет") + "\n"
    res += "**Дома:** " + (", ".join(u['houses']) if u['houses'] else "Нет") + "\n"
    res += "**Акции:** Apple: " + str(u['stocks']['apple']) + ", Google: " + str(u['stocks']['google'])
    await m.answer(res)

# --- [ ЭКОНОМИКА: РАБОТА, БАНК, КРИПТА ] ---

@dp.message(F.text.lower() == ".работа")
async def job_logic(m: types.Message):
    u = get_u(m)
    if datetime.now() - u["last_work"] < timedelta(minutes=3):
        return await m.answer("⏳ Ты устал. Подожди 3 минуты!")
    
    pay = random.randint(5000, 15000)
    tax_v = int(pay * (global_state['tax'] / 100))
    u["balance"] += (pay - tax_v)
    u["last_work"] = datetime.now()
    u["exp"] += 150
    if u["exp"] >= u["lvl"] * 1000: u["lvl"] += 1; u["exp"] = 0
    await m.answer(f"⚒ Ты отработал смену!\n💰 Начислено: `{pay:,}`\n💸 Налог ({global_state['tax']}%): `{tax_v:,}`\n✅ Итого: **{pay-tax_v:,} 💰**")

@dp.message(F.text.lower().startswith(".банк"))
async def bank_put(m: types.Message):
    u = get_u(m)
    try:
        val = int(m.text.split()[1])
        if u["balance"] >= val > 0:
            u["balance"] -= val; u["bank"] += val
            await m.answer(f"🏦 Внесено на депозит: `{val:,}`")
        else: await m.answer("❌ Недостаточно средств!")
    except: await m.answer("❓ Юзай: `.банк 1000`")

@dp.message(F.text.lower().startswith(".снять"))
async def bank_out(m: types.Message):
    u = get_u(m)
    try:
        val = int(m.text.split()[1])
        if u["bank"] >= val > 0:
            u["bank"] -= val; u["balance"] += val
            await m.answer(f"🏦 Снято со счета: `{val:,}`")
        else: await m.answer("❌ В банке нет такой суммы!")
    except: await m.answer("❓ Юзай: `.снять 1000`")

@dp.message(F.text.lower() == ".биржа")
async def stock_market(m: types.Message):
    # Рандомное изменение курса при каждом просмотре
    for key in rates: rates[key] += random.randint(-500, 500)
    txt = (
        "📈 **БИРЖА КРИПТОВАЛЮТ И АКЦИЙ**\n\n"
        f"₿ Bitcoin: `{rates['btc']:,}` 💰\n"
        f"Ξ Ethereum: `{rates['eth']:,}` 💰\n"
        f"🍎 Apple: `{rates['apple']:,}` 💰\n"
        f"🔍 Google: `{rates['google']:,}` 💰\n\n"
        "🔹 Купить: `.купить бтс 1` или `.купить акцию apple 5`"
    )
    await m.answer(txt, parse_mode="Markdown")

# --- [ КАЗИНО И ИГРЫ ] ---

@dp.message(F.text.lower().startswith(".казино"))
async def casino_logic(m: types.Message):
    u = get_u(m)
    try:
        bet = int(m.text.split()[1])
        if u["balance"] < bet or bet < 100: return await m.answer("❌ Ставка неверна!")
        if random.random() < 0.44:
            u["balance"] += bet
            await m.answer(f"🎰 **ПОБЕДА!** Твой выигрыш: `{bet*2:,}` 💰")
        else:
            u["balance"] -= bet
            await m.answer(f"🌚 **ПРОИГРЫШ.** Потеряно: `{bet:,}` 💰")
    except: await m.answer("❓ Пример: `.казино 1000`")

# --- [ ПОЛИТИКА И ВЫБОРЫ ] ---

@dp.message(F.text.lower() == ".выборы")
async def election_info(m: types.Message):
    txt = "🗳 **ВЫБОРЫ ПРЕЗИДЕНТА**\n\n"
    if not votes: txt += "Пока голосов нет. Стань первым!\n"
    else:
        for cid, count in votes.items():
            txt += f"ID {cid}: {count} голосов\n"
    txt += "\n👉 Чтобы проголосовать: `.голосовать [ID_игрока]`"
    await m.answer(txt)

@dp.message(F.text.lower().startswith(".голосовать"))
async def vote_logic(m: types.Message):
    uid = m.from_user.id
    try:
        target_id = int(m.text.split()[1])
        votes[target_id] = votes.get(target_id, 0) + 1
        await m.answer(f"✅ Вы проголосовали за игрока {target_id}!")
    except: pass

# --- [ АДМИН-ПАНЕЛЬ И СЕКРЕТНЫЕ КОМАНДЫ ] ---

@dp.message(Command("ahelp"))
async def adm_help(m: types.Message):
    if not await check_admin(m): return
    txt = (
        "👑 **SECRET OWNER PANEL**\n"
        "• `.выдать [сумма]` — Дать денег (в ответ)\n"
        "• `.уб [сумма]` — Сетнуть баланс (в ответ)\n"
        "• `.статус [текст]` — Дать статус (в ответ)\n"
        "• `.бан` — Бан (в ответ)\n"
        "• `.мут [мин]` — Мут (в ответ)\n"
        "• `/setlvl [lvl]` — Поставить уровень (себе или в ответ)"
    )
    await m.answer(txt)

@dp.message(Command("setlvl"))
async def secret_lvl(m: types.Message):
    if not await check_admin(m): return
    try:
        new_lvl = int(m.text.split()[1])
        target = get_u(m.reply_to_message) if m.reply_to_message else get_u(m)
        target["lvl"] = new_lvl
        await m.answer(f"🔮 Уровень {target['name']} изменен на {new_lvl}")
    except: pass

@dp.message(F.text.lower().startswith(".уб"))
async def adm_set_bal(m: types.Message):
    if not await check_admin(m): return
    if not m.reply_to_message: return await m.answer("❌ Ответь на сообщение!")
    val = int(m.text.split()[-1])
    target = get_u(m.reply_to_message)
    target["balance"] = val
    await m.answer(f"✅ Баланс {target['name']} изменен на `{val:,}`")

@dp.message(F.text.lower().startswith(".бан"))
async def adm_ban(m: types.Message):
    if not await check_admin(m): return
    if not m.reply_to_message: return
    tid = m.reply_to_message.from_user.id
    banned_users.add(tid)
    await m.answer("🚫 Игрок забанен навсегда.")

@dp.message(F.text.lower().startswith(".мут"))
async def adm_mute(m: types.Message):
    if not await check_admin(m): return
    if not m.reply_to_message: return
    mins = int(m.text.split()[-1])
    tid = m.reply_to_message.from_user.id
    muted_users[tid] = datetime.now() + timedelta(minutes=mins)
    await m.answer(f"🤐 Игрок замучен на {mins} мин.")

@dp.message(F.text.lower() == ".админы")
async def show_admins_list(m: types.Message):
    adms = [f"• {u['name']} (@{u['user']})" for i, u in users.items() if u['is_admin']]
    await m.answer("🛡 **ДЕЙСТВУЮЩАЯ АДМИНИСТРАЦИЯ:**\n" + "\n".join(adms))

@dp.message(F.text.lower() == ".топ")
async def show_forbes_top(m: types.Message):
    top = sorted(users.items(), key=lambda x: x[1]['balance'] + x[1]['bank'], reverse=True)[:10]
    res = "🏆 **FORBES GLOBAL TOP:**\n\n"
    for i, (uid, d) in enumerate(top, 1):
        res += f"{i}. {d['name']} — `{d['balance']+d['bank']:,}` 💰\n"
    await m.answer(res)

# --- [ МАГАЗИН И ПОКУПКИ ] ---
@dp.message(F.text.lower() == ".магазин")
async def shop_full(m: types.Message):
    txt = "🛒 **ЦЕНТРАЛЬНЫЙ УНИВЕРМАГ**\n\n**🚗 МАШИНЫ:**\n"
    for k, v in CARS.items(): txt += f"• {k}: `{v:,}`\n"
    txt += "\n**🏠 ДОМА:**\n"
    for k, v in HOUSES.items(): txt += f"• {k}: `{v:,}`\n"
    txt += "\n**🏢 БИЗНЕС:**\n"
    for k, v in BUSINESS.items(): txt += f"• {k}: `{v:,}`\n"
    txt += "\n👉 Купить: `.купить [название]`"
    await m.answer(txt)

@dp.message(F.text.lower().startswith(".купить"))
async def buy_engine(m: types.Message):
    u = get_u(m)
    item = m.text.replace(".купить", "").strip()
    # Логика покупки тачек
    if item in CARS:
        if u["balance"] >= CARS[item]:
            u["balance"] -= CARS[item]; u["cars"].append(item)
            await m.answer(f"✅ Куплено: {item}")
        else: await m.answer("❌ Денег нет!")
    # Логика крипты
    elif "бтс" in item.lower():
        try:
            amt = int(item.split()[-1])
            cost = rates["btc"] * amt
            if u["balance"] >= cost:
                u["balance"] -= cost; u["btc"] += amt
                await m.answer(f"₿ Куплено {amt} BTC!")
            else: await m.answer("❌ Не хватает на крипту!")
        except: pass
    else: await m.answer("❌ Товар не найден.")

# --- [ ЗАПУСК ] ---
async def main():
    await set_main_menu(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
