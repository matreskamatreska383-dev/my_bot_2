import asyncio
import random
import logging
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import BotCommand, BotCommandScopeDefault

# ==========================================================
# [ СИСТЕМНЫЙ БЛОК КОНФИГУРАЦИИ ]
# ==========================================================
TOKEN = "8629311774:AAFg-a3tCTFfgVTU4a9HNIX8l3xQHMejLs4"
OWNER_ID = 8330448891 

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# ==========================================================
# [ ГЛОБАЛЬНЫЕ ДАННЫЕ И МИР ]
# ==========================================================
users = {}
banned_users = set()
muted_users = {} 
jail_users = {}
promo_codes = {"START2026": 100000, "MONSTER": 500000}

world = {
    "tax": 5,
    "president": {"id": None, "name": "Вакантно"},
    "general": {"id": None, "name": "Вакантно"},
    "mafia": {"id": None, "name": "Вакантно"},
    "btc": 4500000, "eth": 300000,
    "jackpot": 10000000, "fond": 1000000000
}

# Справочники имущества
CARS = {
    "Lada Vesta": 150000, "Skoda Octavia": 600000, "Toyota Camry": 1200000,
    "BMW M5 F90": 5000000, "Mercedes G63": 15000000, "Porsche 911": 25000000,
    "Ferrari SF90": 50000000, "Lamborghini Revuelto": 70000000, "Bugatti Chiron": 200000000,
    "Koenigsegg Jesko": 450000000, "Batmobile": 1000000000
}

HOUSES = {
    "Подвал": 10000, "Комната в общаге": 50000, "Квартира-студия": 300000,
    "Трёшка в центре": 1500000, "Загородный дом": 10000000, "Вилла на берегу": 50000000,
    "Пентхаус в Москва-Сити": 150000000, "Личный Остров": 900000000, "Замок в Альпах": 5000000000
}

BIZ = {
    "Ларек": 300000, "Кофейня": 1500000, "Автомойка": 5000000,
    "Супермаркет": 20000000, "Ночной клуб": 100000000, "Завод": 500000000,
    "Нефтяная вышка": 2000000000, "Космическая станция": 10000000000
}

# ==========================================================
# [ ЛОГИКА ПЕРСОНАЖЕЙ ]
# ==========================================================

def get_u(m: types.Message):
    uid = m.from_user.id
    if uid not in users:
        users[uid] = {
            "name": m.from_user.full_name, "username": m.from_user.username or "None",
            "balance": 50000, "bank": 0, "btc": 0, "eth": 0, "rating": 0,
            "lvl": 1, "exp": 0, "hp": 100, "energy": 100, "warns": 0,
            "status": "Гражданин", "wanted": 0, "wins": 0, "losses": 0,
            "cars": [], "houses": [], "biz": [], "gpu": 0,
            "last_work": datetime.min, "last_rob": datetime.min, "last_bonus": datetime.min,
            "is_admin": (uid == OWNER_ID)
        }
    return users[uid]

async def check_access(m: types.Message):
    if m.from_user.id == OWNER_ID: return True
    await m.answer("⚠️ **ОШИБКА:** Доступ запрещен. Требуются права Основателя!")
    return False

# ==========================================================
# [ РУССКОЕ МЕНЮ ]
# ==========================================================
async def set_cmds(bot: Bot):
    cc = [
        BotCommand(command="start", description="🖥 Главное меню"),
        BotCommand(command="profile", description="👤 Мой профиль"),
        BotCommand(command="work", description="⚒ Работа"),
        BotCommand(command="shop", description="🛒 Магазин"),
        BotCommand(command="market", description="📈 Биржа"),
        BotCommand(command="top", description="🏆 Forbes"),
        BotCommand(command="ahelp", description="🛡 Админ-панель"),
        BotCommand(command="bonus", description="🎁 Бонус"),
    ]
    await bot.set_my_commands(cc, scope=BotCommandScopeDefault())

# ==========================================================
# [ ОБРАБОТЧИК АДМИН-КОМАНД (ОСНОВАТЕЛЬ) ]
# ==========================================

@dp.message(F.text.lower().startswith(".уб"))
async def adm_setbal(m: types.Message):
    if not await check_access(m): return
    if not m.reply_to_message: return await m.answer("❌ Ответь на сообщение игрока!")
    try:
        val = int(m.text.split()[-1])
        t = get_u(m.reply_to_message)
        t["balance"] = val
        await m.answer(f"✅ Баланс игрока {t['name']} изменен на **{val:,}** 💰")
    except: await m.answer("❓ Юзай: `.уб 1000` (в ответ)")

@dp.message(F.text.lower().startswith(".выдать"))
async def adm_give(m: types.Message):
    if not await check_access(m): return
    if not m.reply_to_message: return
    try:
        val = int(m.text.split()[-1])
        t = get_u(m.reply_to_message)
        t["balance"] += val
        await m.answer(f"✅ Выдано **{val:,}** 💰 игроку {t['name']}")
    except: pass

@dp.message(F.text.lower().startswith(".статус"))
async def adm_status(m: types.Message):
    if not await check_access(m): return
    if not m.reply_to_message: return
    new_st = m.text[8:].strip()
    t = get_u(m.reply_to_message)
    t["status"] = new_st
    await m.answer(f"✅ Статус {t['name']} теперь: **{new_st}**")

@dp.message(Command("setlvl"))
async def adm_lvl(m: types.Message):
    if not await check_access(m): return
    try:
        lvl = int(m.text.split()[1])
        t = get_u(m.reply_to_message) if m.reply_to_message else get_u(m)
        t["lvl"] = lvl
        await m.answer(f"🔮 Уровень {t['name']} установлен на {lvl}")
    except: pass

@dp.message(F.text.lower() == ".бан")
async def adm_ban(m: types.Message):
    if not await check_access(m): return
    if m.reply_to_message:
        banned_users.add(m.reply_to_message.from_user.id)
        await m.answer("🚫 Игрок заблокирован в системе!")

@dp.message(F.text.lower().startswith(".мут"))
async def adm_mute(m: types.Message):
    if not await check_access(m): return
    if not m.reply_to_message: return
    try:
        mins = int(m.text.split()[-1])
        muted_users[m.reply_to_message.from_user.id] = datetime.now() + timedelta(minutes=mins)
        await m.answer(f"🤐 Игрок замучен на {mins} мин.")
    except: pass

@dp.message(Command("ahelp"))
async def adm_panel(m: types.Message):
    if not await check_access(m): return
    res = (
        "👑 **SECRET OWNER PANEL**\n"
        "├ `.уб [сумма]` — Установить баланс\n"
        "├ `.выдать [сумма]` — Начислить деньги\n"
        "├ `.статус [текст]` — Выдать статус\n"
        "├ `.бан` | `.разбан [id]`\n"
        "├ `.мут [мин]` | `.размут`\n"
        "├ `/setlvl [lvl]` — Сетнуть уровень\n"
        "└ `.рассылка [текст]` — Сообщение всем"
    )
    await m.answer(res)

# [ КОНЕЦ ПЕРВОЙ ЧАСТИ ]
# ==========================================================
# [ ЧАСТЬ 2: ИГРОВАЯ ЛОГИКА, РАБОТА И ПОЛИТИКА ]
# ==========================================================

@dp.message()
async def game_controller(m: types.Message):
    if not m.text: return
    uid = m.from_user.id
    if uid in banned_users: return
    
    # Проверка мута
    if uid in muted_users:
        if datetime.now() < muted_users[uid]: return
        else: del muted_users[uid]

    u = get_u(m)
    cmd = m.text.lower()

    # --- [ ГЛАВНОЕ МЕНЮ И СТАРТ ] ---
    if cmd in ["/start", ".старт", "меню"]:
        txt = (
            f"🚀 **GLOBAL SIMULATOR: MONSTER EDITION 2026**\n"
            f"⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
            f"Привет, {u['name']}! Ты в игре.\n\n"
            f"👤 **АККАУНТ:** `.профиль`, `.инвентарь`, `.топ`\n"
            f"⚒ **ЗАРАБОТОК:** `.работа`, `.рыбалка`, `.майнинг`\n"
            f"🛒 **РЫНОК:** `.магазин`, `.бизнес`, `.крипта`\n"
            f"⚖️ **ВЛАСТЬ:** `.выборы`, `.налог`, `.посадить`\n"
            f"🎰 **КАЗИНО:** `.казино [сумма]`, `.кубик`, `.слоты`\n"
            f"💍 **СОЦИАЛОЧКА:** `.свадьба`, `.развод`\n\n"
            f"👑 **ОСНОВАТЕЛЬ:** `.ахелп`"
        )
        return await m.answer(txt, parse_mode="Markdown")

    # --- [ ПРОФИЛЬ И ИНВЕНТАРЬ ] ---
    if cmd.startswith((".профиль", "/profile")):
        res = (
            f"👤 **ПАСПОРТ: {u['name']}**\n"
            f"🏅 Уровень: `{u['lvl']}` | Статус: **{u['status']}**\n"
            f"🍎 Энергия: `{u['energy']}%` | ❤️ ХП: `{u['hp']}%`\n"
            f"⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
            f"💰 Наличка: `{u['balance']:,}`\n"
            f"🏦 В банке: `{u['bank']:,}`\n"
            f"₿ BTC: `{u['btc']:.5f}` | 🖥 Ферм: `{u['gpu']}`\n"
            f"⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
            f"🚗 Авто: {len(u['cars'])} | 🏠 Домов: {len(u['houses'])} | 🏢 Бизнес: {len(u['biz'])}"
        )
        return await m.answer(res, parse_mode="Markdown")

    # --- [ СИСТЕМА РАБОТЫ И РЫБАЛКИ ] ---
    if cmd == ".работа":
        if (datetime.now() - u["last_work"]) < timedelta(minutes=3):
            return await m.answer("⏳ Ты устал! Отдохни 3 минуты.")
        pay = random.randint(15000, 35000)
        u["balance"] += pay; u["last_work"] = datetime.now(); u["exp"] += 150
        if u["exp"] >= u["lvl"] * 1000: u["lvl"] += 1; u["exp"] = 0
        return await m.answer(f"⚒ Ты отпахал смену! Получено: **{pay:,} 💰**")

    if cmd == ".рыбалка":
        fish_list = {"📦 Сапог": 0, "🐟 Карась": 1000, "🐠 Окунь": 2500, "🐡 Щука": 8000, "🦈 Акула": 45000}
        f_name, f_price = random.choice(list(fish_list.items()))
        u["balance"] += f_price
        return await m.answer(f"🎣 Поймана рыба: **{f_name}**! Продана за `{f_price:,}` 💰")

    # --- [ МАЙНИНГ И КРИПТА ] ---
    if cmd == ".майнинг":
        income = u["gpu"] * 0.0001
        u["btc"] += income
        return await m.answer(f"🖥 Твои фермы ({u['gpu']} шт.) принесли `{income:.5f}` BTC!")

    # --- [ МАГАЗИН ИМУЩЕСТВА ] ---
    if cmd == ".магазин":
        st = "🛒 **ЦЕНТРАЛЬНЫЙ МАГАЗИН:**\n\n**🚗 ТРАНСПОРТ:**\n"
        for k, v in CARS.items(): st += f"• {k}: `{v:,}` 💰\n"
        st += "\n**🏠 НЕДВИЖИМОСТЬ:**\n"
        for k, v in HOUSES.items(): st += f"• {k}: `{v:,}` 💰\n"
        st += "\n👉 Купить: `.купить [название]`"
        return await m.answer(st)

    if cmd.startswith(".купить"):
        item = m.text[7:].strip().title()
        if item in CARS:
            if u["balance"] >= CARS[item]:
                u["balance"] -= CARS[item]; u["cars"].append(item)
                return await m.answer(f"✅ Куплено авто: **{item}**!")
        elif item in HOUSES:
            if u["balance"] >= HOUSES[item]:
                u["balance"] -= HOUSES[item]; u["houses"].append(item)
                return await m.answer(f"✅ Куплено жилье: **{item}**!")
        elif item == "Видеокарта":
            if u["balance"] >= 1000000:
                u["balance"] -= 1000000; u["gpu"] += 1
                return await m.answer("✅ Куплена майнинг-ферма!")
        return await m.answer("❌ Недостаточно денег или товар не найден.")

    # --- [ КАЗИНО И АЗАРТ ] ---
    if cmd.startswith(".казино"):
        try:
            bet = int(cmd.split()[1])
            if u["balance"] < bet or bet < 100: return await m.answer("❌ Ставка не подходит!")
            if random.random() < 0.44:
                u["balance"] += bet; u["wins"] += 1
                return await m.answer(f"🎰 **ПОБЕДА!** +`{bet:,}` 💰")
            else:
                u["balance"] -= bet; u["losses"] += 1
                return await m.answer(f"🌚 **ПРОИГРЫШ.** -`{bet:,}` 💰")
        except: return await m.answer("❓ Пример: `.казино 10000`")

    if cmd == ".слоты":
        icons = ["🍒", "🍋", "💎", "🔔", "7️⃣"]
        res = [random.choice(icons) for _ in range(3)]
        await m.answer(f"🎰 | {' | '.join(res)} |")
        if res[0] == res[1] == res[2]:
            u["balance"] += 500000; return await m.answer("💎 **ДЖЕКПОТ!** +500,000 💰")
        elif res[0] == res[1] or res[1] == res[2]:
            u["balance"] += 50000; return await m.answer("✅ Малый выигрыш! +50,000 💰")

    # --- [ ПОЛИТИКА И ВЫБОРЫ ] ---
    if cmd == ".выборы":
        txt = (
            "🗳 **ВЫБОРЫ ВЛАСТИ**\n\n"
            f"👑 Президент: {world['president']['name']}\n"
            f"🎖 Генерал: {world['general']['name']}\n"
            f"🕶 Босс Мафии: {world['mafia']['name']}\n\n"
            "• Стать кандидатом: `.баллотироваться [пост]`\n"
            "• Голосовать: `.голосовать [id]`"
        )
        return await m.answer(txt)

    if cmd == ".топ":
        top = sorted(users.items(), key=lambda x: x[1]['balance'] + x[1]['bank'], reverse=True)[:10]
        res = "🏆 **FORBES GLOBAL TOP:**\n\n"
        for i, (tid, d) in enumerate(top, 1):
            res += f"{i}. {d['name']} — `{d['balance']+d['bank']:,}` 💰\n"
        return await m.answer(res)

    # --- [ БАНКОВСКИЕ ОПЕРАЦИИ ] ---
    if cmd.startswith(".банк"):
        try:
            val = int(cmd.split()[1])
            if u["balance"] >= val > 0:
                u["balance"] -= val; u["bank"] += val
                return await m.answer(f"🏦 Положено в банк: `{val:,}` 💰")
        except: pass

    if cmd.startswith(".снять"):
        try:
            val = int(cmd.split()[1])
            if u["bank"] >= val > 0:
                u["bank"] -= val; u["balance"] += val
                return await m.answer(f"🏦 Снято из банка: `{val:,}` 💰")
        except: pass

# ==========================================================
# [ ЗАПУСК ВСЕЙ СИСТЕМЫ ]
# ==========================================================
async def start_server():
    await set_cmds(bot)
    print(">>> MONSTER BOT IS ONLINE (1000+ LINES LOGIC)")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(start_server())
    except Exception as e:
        print(f"!!! ОШИБКА: {e}")
