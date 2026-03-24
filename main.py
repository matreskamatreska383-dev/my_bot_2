import asyncio
import random
import logging
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import BotCommand, BotCommandScopeDefault, ReplyKeyboardRemove

# --- [ ПОЛНАЯ КОНФИГУРАЦИЯ СИСТЕМЫ ] ---
TOKEN = "8629311774:AAFg-a3tCTFfgVTU4a9HNIX8l3xQHMejLs4"
OWNER_ID = 8330448891 

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- [ ГЛОБАЛЬНАЯ БАЗА ДАННЫХ В ПАМЯТИ ] ---
users = {}
banned_users = set()
muted_users = {} # {id: datetime}
votes = {} # {candidate_id: [voter_ids]}

# Экономические показатели
market = {
    "btc": 4500000, 
    "eth": 280000, 
    "apple": 15000, 
    "tesla": 85000,
    "tax": 5,
    "president": None
}

# Списки имущества
CARS = {
    "Lada Granta": 150000, "Solaris": 800000, "BMW M5": 4500000, 
    "Mercedes G63": 12000000, "Ferrari Purosangue": 45000000, "Bugatti Chiron": 120000000
}
HOUSES = {
    "Бытовка": 45000, "Квартира в хрущевке": 450000, "Пентхаус": 15000000, 
    "Вилла в Дубае": 85000000, "Личный замок": 350000000, "Небоскреб": 1200000000
}
BIZ = {
    "Шаурмичная": 250000, "Магазин 24/7": 1200000, "Автосалон": 15000000, 
    "Нефтяная вышка": 500000000, "Банк": 2000000000
}

# --- [ ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ] ---

def get_u(m: types.Message):
    uid = m.from_user.id
    if uid not in users:
        users[uid] = {
            "name": m.from_user.full_name,
            "username": m.from_user.username or "None",
            "balance": 30000, "bank": 0, "btc": 0, "eth": 0,
            "stocks": {"apple": 0, "tesla": 0},
            "lvl": 1, "exp": 0, "energy": 100, "hp": 100,
            "status": "Игрок", "cars": [], "houses": [], "biz": [],
            "last_work": datetime.min, "is_admin": False
        }
    if uid == OWNER_ID: users[uid]["is_admin"] = True
    return users[uid]

async def is_owner(m: types.Message):
    if m.from_user.id == OWNER_ID:
        return True
    await m.answer("⚠️ **ОТКАЗАНО:** У вас нет прав Основателя для этой команды!")
    return False

# --- [ СИСТЕМА КОМАНД И МЕНЮ ] ---

async def set_main_menu(bot: Bot):
    main_commands = [
        BotCommand(command="start", description="🖥 Главное меню"),
        BotCommand(command="profile", description="👤 Мой профиль"),
        BotCommand(command="work", description="⚒ Работа"),
        BotCommand(command="shop", description="🛒 Магазин"),
        BotCommand(command="market", description="📈 Биржа"),
        BotCommand(command="casino", description="🎰 Казино"),
        BotCommand(command="top", description="🏆 Forbes"),
        BotCommand(command="vote", description="🗳 Выборы"),
        BotCommand(command="ahelp", description="🛡 Админ-панель")
    ]
    await bot.set_my_commands(main_commands, scope=BotCommandScopeDefault())

# --- [ ОБРАБОТКА МУТА И БАНА (MIDDLEWARE) ] ---

@dp.message()
async def global_handler(m: types.Message):
    uid = m.from_user.id
    # Проверка бана
    if uid in banned_users:
        return
    # Проверка мута
    if uid in muted_users:
        if datetime.now() < muted_users[uid]:
            return # Просто игнорим
        else:
            del muted_users[uid]

    # Обработка команд вручную для поддержки точки
    text = m.text.lower() if m.text else ""
    u = get_u(m)

    # --- [ БЛОК: СТАРТ И ИНФО ] ---
    if text in ["/start", ".старт"]:
        return await m.answer(
            "🏙 **GLOBAL SIMULATOR: OVERDRIVE 2.0**\n"
            "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
            "Добро пожаловать в самый мощный симулятор в Telegram!\n\n"
            "🎮 **ИГРОВЫЕ КОМАНДЫ:**\n"
            "• `.профиль` | `.инвентарь` | `.топ`\n"
            "• `.работа` | `.банк` | `.снять`\n"
            "• `.биржа` | `.крипта` | `.акции`\n"
            "• `.магазин` | `.бизнес` | `.купить [имя]`\n"
            "• `.казино [ставка]` | `.кубик` | `.слоты`\n\n"
            "🗳 **ПОЛИТИКА:** `.выборы`, `.голосовать [id]`\n"
            "🛡 **АДМИНКА:** `.ахелп` (Только для Основателя)",
            parse_mode="Markdown"
        )

    # --- [ БЛОК: ПРОФИЛЬ ] ---
    if text.startswith((".профиль", "/profile")):
        txt = (
            f"👤 **ПАСПОРТ: {u['name']}**\n"
            f"🏅 Уровень: `{u['lvl']}` ({u['exp']}/{(u['lvl']*1000)})\n"
            f"🎭 Статус: **{u['status']}**\n"
            f"🍎 Энергия: `{u['energy']}%` | ❤️ ХП: `{u['hp']}%`\n"
            f"⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
            f"💰 Наличные: `{u['balance']:,}` 💰\n"
            f"🏦 В банке: `{u['bank']:,}` 💰\n"
            f"₿ BTC: `{u['btc']:.4f}` | Ξ ETH: `{u['eth']:.2f}`\n"
            f"⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
            f"🚗 Авто: {len(u['cars'])} | 🏠 Дома: {len(u['houses'])} | 🏢 Бизнес: {len(u['biz'])}"
        )
        return await m.answer(txt, parse_mode="Markdown")

    # --- [ БЛОК: ЭКОНОМИКА ] ---
    if text == ".работа":
        if datetime.now() - u["last_work"] < timedelta(minutes=3):
            wait = timedelta(minutes=3) - (datetime.now() - u["last_work"])
            return await m.answer(f"⏳ Вы устали! Отдохните еще {wait.seconds} сек.")
        
        pay = random.randint(5000, 15000)
        tax_amt = int(pay * (market['tax'] / 100))
        u["balance"] += (pay - tax_amt)
        u["last_work"] = datetime.now()
        u["exp"] += 150
        if u["exp"] >= u["lvl"] * 1000:
            u["lvl"] += 1; u["exp"] = 0
            await m.answer("🆙 **LEVEL UP!** Ваш уровень теперь: " + str(u["lvl"]))
        return await m.answer(f"⚒ Ты отработал смену!\n💰 Грязными: `{pay:,}`\n💸 Налог ({market['tax']}%): `{tax_amt:,}`\n✅ Получено: **{pay-tax_amt:,} 💰**")

    if text.startswith(".банк"):
        try:
            amt = int(text.split()[1])
            if u["balance"] >= amt > 0:
                u["balance"] -= amt; u["bank"] += amt
                return await m.answer(f"🏦 Депозит пополнен на `{amt:,}` 💰")
            else: return await m.answer("❌ Недостаточно наличных!")
        except: return await m.answer("❓ Пример: `.банк 1000`")

    if text.startswith(".снять"):
        try:
            amt = int(text.split()[1])
            if u["bank"] >= amt > 0:
                u["bank"] -= amt; u["balance"] += amt
                return await m.answer(f"🏦 Снято со счета: `{amt:,}` 💰")
            else: return await m.answer("❌ В банке нет столько денег!")
        except: return await m.answer("❓ Пример: `.снять 1000`")

    # --- [ БЛОК: БИРЖА (КРИПТА И АКЦИИ) ] ---
    if text == ".биржа":
        # Динамика цен
        market["btc"] += random.randint(-100000, 100000)
        market["apple"] += random.randint(-500, 500)
        txt = (
            "📈 **МИРОВАЯ БИРЖА**\n\n"
            f"₿ Bitcoin (BTC): `{market['btc']:,}` 💰\n"
            f"Ξ Ethereum (ETH): `{market['eth']:,}` 💰\n"
            f"🍎 Акция Apple: `{market['apple']:,}` 💰\n"
            f"🚗 Акция Tesla: `{market['tesla']:,}` 💰\n\n"
            "🔹 Купить: `.купить бтс 1` или `.купить акцию тесла 5`"
        )
        return await m.answer(txt, parse_mode="Markdown")

    # --- [ БЛОК: МАГАЗИН И ПОКУПКИ ] ---
    if text == ".магазин":
        res = "🛒 **МАГАЗИН ВСЕГО:**\n\n**🚗 МАШИНЫ:**\n"
        for k, v in CARS.items(): res += f"• {k}: `{v:,}` 💰\n"
        res += "\n**🏠 ДОМА:**\n"
        for k, v in HOUSES.items(): res += f"• {k}: `{v:,}` 💰\n"
        res += "\n**🏢 БИЗНЕС:**\n"
        for k, v in BIZ.items(): res += f"• {k}: `{v:,}` 💰\n"
        res += "\n👉 Купить: `.купить [название]`"
        return await m.answer(res)

    if text.startswith(".купить"):
        item = text.replace(".купить", "").strip()
        if item in CARS:
            if u["balance"] >= CARS[item]:
                u["balance"] -= CARS[item]; u["cars"].append(item)
                return await m.answer(f"🚗 Поздравляем с покупкой **{item}**!")
            else: return await m.answer("❌ Нет денег!")
        elif item in HOUSES:
            if u["balance"] >= HOUSES[item]:
                u["balance"] -= HOUSES[item]; u["houses"].append(item)
                return await m.answer(f"🏠 Теперь у вас есть свой дом: **{item}**!")
            else: return await m.answer("❌ Нет денег!")
        elif item in BIZ:
            if u["balance"] >= BIZ[item]:
                u["balance"] -= BIZ[item]; u["biz"].append(item)
                return await m.answer(f"🏢 Вы открыли бизнес: **{item}**!")
            else: return await m.answer("❌ Нет денег!")
        # Покупка крипты
        elif "бтс" in item:
            try:
                count = int(item.split()[-1])
                cost = market["btc"] * count
                if u["balance"] >= cost:
                    u["balance"] -= cost; u["btc"] += count
                    return await m.answer(f"₿ Куплено BTC: {count} шт.")
            except: pass
        return await m.answer("❌ Товар не найден. Проверьте название в `.магазин`")

    # --- [ БЛОК: КАЗИНО ] ---
    if text.startswith(".казино"):
        try:
            bet = int(text.split()[1])
            if u["balance"] < bet or bet < 100: return await m.answer("❌ Ставка слишком мала или нет денег!")
            if random.random() < 0.44:
                u["balance"] += bet
                return await m.answer(f"🎰 **ПОБЕДА!** Ваш выигрыш: `{bet*2:,}` 💰")
            else:
                u["balance"] -= bet
                return await m.answer(f"🌚 **ПРОИГРЫШ.** Вы потеряли `{bet:,}` 💰")
        except: return await m.answer("❓ Пример: `.казино 5000`")

    # --- [ БЛОК: РЕЙТИНГ ] ---
    if text == ".топ":
        top = sorted(users.items(), key=lambda x: x[1]['balance'] + x[1]['bank'], reverse=True)[:10]
        res = "🏆 **FORBES GLOBAL TOP:**\n\n"
        for i, (uid, d) in enumerate(top, 1):
            total = d['balance'] + d['bank']
            res += f"{i}. {d['name']} — `{total:,}` 💰\n"
        return await m.answer(res)

    # --- [ БЛОК: ПОЛИТИКА ] ---
    if text == ".выборы":
        txt = "🗳 **ВЫБОРЫ ПРЕЗИДЕНТА**\n\nКандидаты:\n"
        for cid, voters in votes.items():
            txt += f"• ID {cid}: {len(voters)} голосов\n"
        txt += "\n👉 Проголосовать: `.голосовать [ID]`"
        return await m.answer(txt)

    if text.startswith(".голосовать"):
        try:
            target_id = int(text.split()[1])
            if target_id not in votes: votes[target_id] = []
            if uid not in [v for sub in votes.values() for v in sub]:
                votes[target_id].append(uid)
                return await m.answer("✅ Голос принят!")
            else: return await m.answer("❌ Вы уже голосовали!")
        except: pass

    # --- [ БЛОК: АДМИН ПАНЕЛЬ (ТОЛЬКО ОСНОВАТЕЛЬ) ] ---
    if text in [".ахелп", "/ahelp", ".админ"]:
        if not await is_owner(m): return
        txt = (
            "🛡 **ПАНЕЛЬ ОСНОВАТЕЛЯ**\n\n"
            "• `.выдать [сумма]` — Дать денег (реплаем)\n"
            "• `.уб [сумма]` — Установить баланс (реплаем)\n"
            "• `.статус [текст]` — Выдать статус (реплаем)\n"
            "• `.бан` — Бан навсегда (реплаем)\n"
            "• `.разбан [id]` — Снять бан\n"
            "• `.мут [мин]` — Мут игрока (реплаем)\n"
            "• `/setlvl [число]` — Сетнуть лвл (себе или реплаем)\n"
            "• `.налог [0-30]` — Установить налог"
        )
        return await m.answer(txt)

    if text.startswith("/setlvl"):
        if not await is_owner(m): return
        try:
            lvl = int(text.split()[1])
            target = get_u(m.reply_to_message) if m.reply_to_message else u
            target["lvl"] = lvl
            return await m.answer(f"🔮 Уровень {target['name']} изменен на {lvl}")
        except: pass

    if text.startswith(".уб"):
        if not await is_owner(m): return
        if not m.reply_to_message: return
        try:
            val = int(text.split()[-1])
            target = get_u(m.reply_to_message)
            target["balance"] = val
            return await m.answer(f"✅ Баланс {target['name']} изменен на {val}")
        except: pass

    if text.startswith(".бан"):
        if not await is_owner(m): return
        if not m.reply_to_message: return
        tid = m.reply_to_message.from_user.id
        banned_users.add(tid)
        return await m.answer("🚫 Игрок заблокирован.")

    if text.startswith(".мут"):
        if not await is_owner(m): return
        if not m.reply_to_message: return
        try:
            mins = int(text.split()[-1])
            tid = m.reply_to_message.from_user.id
            muted_users[tid] = datetime.now() + timedelta(minutes=mins)
            return await m.answer(f"🤐 Игрок замучен на {mins} минут.")
        except: pass

    if text.startswith(".налог"):
        if not await is_owner(m): return
        try:
            ntax = int(text.split()[-1])
            if 0 <= ntax <= 30:
                market["tax"] = ntax
                return await m.answer(f"📊 Налог изменен на {ntax}%")
        except: pass

    if text == ".админы":
        adms = [f"• {d['name']} (@{d['username']})" for i, d in users.items() if d['is_admin']]
        return await m.answer("🛡 **АДМИНИСТРАЦИЯ:**\n" + "\n".join(adms))

# --- [ ЗАПУСК БОТА ] ---
async def start_up():
    await set_main_menu(bot)
    print(">>> GLOBAL SIMULATOR STARTED (MONSTER MODE)")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(start_up())
    except (KeyboardInterrupt, SystemExit):
        print(">>> BOT STOPPED")
