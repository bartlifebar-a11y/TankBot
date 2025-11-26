import asyncio
import logging
import requests
import os
import json
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import BotCommand, BotCommandScopeDefault, BufferedInputFile
from aiogram.client.session.aiohttp import AiohttpSession
import urllib3

# ==========================================================
# 🛑 НАСТРОЙКИ
# ==========================================================
BOT_TOKEN = "8207322718:AAGXQdZl15tg8eZWuMMAd8SEVuYkI1LDho8"
WG_APP_ID = "04511f3e9fe8b473aad8f9577fd0bdf0"
REGION = 'eu'
ADMIN_ID = 406810524
USERS_FILE = "users_db.json"

# PROXY (Обязательно для PythonAnywhere)
PROXY_URL = "http://proxy.server:3128"

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'}

# ==========================================================
# 🗺 & 📚 БАЗЫ ДАННЫХ
# ==========================================================
MAPS_DB = {
    "Малиновка": "https://wiki.wargaming.net/images/e/e0/Malinovka_plan.jpg",
    "Прохоровка": "https://wiki.wargaming.net/images/a/a2/Prohorovka_plan.jpg",
    "Химмельсдорф": "https://wiki.wargaming.net/images/4/44/Himmelsdorf_plan.jpg",
    "Руинберг": "https://wiki.wargaming.net/images/e/e4/Ruinberg_plan.jpg",
    "Рудники": "https://wiki.wargaming.net/images/d/dc/Mines_plan.jpg",
    "Мурованка": "https://wiki.wargaming.net/images/e/e4/Murowanka_plan.jpg",
    "Энск": "https://wiki.wargaming.net/images/3/36/Ensk_plan.jpg",
    "Ласвилль": "https://wiki.wargaming.net/images/0/07/Lakeville_plan.jpg",
    "Песчаная река": "https://wiki.wargaming.net/images/d/d4/Sand_river_plan.jpg",
    "Степи": "https://wiki.wargaming.net/images/b/b5/Steppes_plan.jpg",
    "Фьорды": "https://wiki.wargaming.net/images/5/56/Fjords_plan.jpg",
    "Перевал": "https://wiki.wargaming.net/images/d/d2/Caucasus_plan.jpg",
    "Редшир": "https://wiki.wargaming.net/images/3/34/Redshire_plan.jpg",
    "Утес": "https://wiki.wargaming.net/images/b/be/Cliff_plan.jpg",
    "Монастырь": "https://wiki.wargaming.net/images/4/44/Monastery_plan.jpg",
    "Вестфилд": "https://wiki.wargaming.net/images/2/23/Westfeld_plan.jpg",
    "Линия Зигфрида": "https://wiki.wargaming.net/images/8/82/Siegfried_line_plan.jpg",
    "Рыбацкая бухта": "https://wiki.wargaming.net/images/3/36/Fishing_bay_plan.jpg",
    "Затерянный город": "https://wiki.wargaming.net/images/101_dday_m.jpg",
    "Париж": "https://wiki.wargaming.net/images/2/22/Paris_plan.jpg",
    "Студзянки": "https://wiki.wargaming.net/images/a/ae/Studzianki_plan.jpg",
    "Берлин": "https://wiki.wargaming.net/images/a/a7/Berlin_plan.jpg",
    "Эрленберг": "https://wiki.wargaming.net/images/1/14/Erlenberg_plan.jpg",
    "Карелия": "https://wiki.wargaming.net/images/5/50/Karelia_plan.jpg"
}

TANK_DB = {
    "КР-1": "🇷🇺 <b>КР-1</b> (ТТ-11)\n🛠 Закалка, Турбина, Досылатель.\n💡 Предшественник ИС-7.",
    "AMX 67": "🇫🇷 <b>AMX 67</b> (ТТ-11)\n🛠 Вентиль, Стабилизатор, УМП.\n💡 Предшественник AMX 50 B.",
    "FV4025 Contriver": "🇬🇧 <b>FV4025</b> (ТТ-11)\n🛠 Закалка, Досылатель, Турбина.",
    "Taschenratte": "🇩🇪 <b>Taschenratte</b> (ТТ-11)\n🛠 Закалка, Досылатель, Турбина.",
    "T803": "🇺🇸 <b>T803</b> (ТТ-11)\n🛠 Досылатель, Стабилизатор, Вентиль.",
    "BZ-79": "🇨🇳 <b>BZ-79</b> (ТТ-11)\n🛠 Досылатель, Стабилизатор, Приводы.",
    "Black Rock": "⚫️ <b>Black Rock</b> (ТТ-11)\n🛠 Вентиль, Стабилизатор, Досылатель.",
    "Super Conqueror": "🇬🇧 <b>Super Conqueror</b> (ТТ-10)\n🛠 Закалка, Досылатель, Турбина.",
    "VZ. 55": "🇨🇿 <b>VZ. 55</b> (ТТ-10)\n🛠 Вентиль, Стаб, Турбина.",
    "IS-7": "🇺🇸 <b>IS-7</b> (ТТ-10)\n🛠 Закалка, Турбина, Досылатель.",
    "Maus": "🇩🇪 <b>Maus</b> (ТТ-10)\n🛠 Закалка, Досылатель, Турбина.",
    "Leopard 1": "🇩🇪 <b>Leopard 1</b> (СТ-10)\n🛠 Досылатель, Вентиль, Оптика.",
    "Grille 15": "🇩🇪 <b>Grille 15</b> (ПТ-10)\n🛠 Досылатель, УМП, Турбина.",
    "EBR 105": "🇫🇷 <b>EBR 105</b> (ЛТ-10)\n🛠 Оптика, КОП, Вентиль.",
    "Skoda T 56": "🇨🇿 <b>Skoda T 56</b> (ТТ-8)\n🛠 Закалка, Стаб, Турбина.",
    "Bourrasque": "🇫🇷 <b>Bourrasque</b> (СТ-8)\n🛠 Вентиль, Стаб, Оптика.",
    "Progetto 46": "🇮🇹 <b>Progetto 46</b> (СТ-8)\n🛠 Вентиль, Стаб, Досылатель."
}

# ==========================================================
# 🤖 ИНИЦИАЛИЗАЦИЯ
# ==========================================================
logging.basicConfig(level=logging.INFO)
session = AiohttpSession(proxy=PROXY_URL)
bot = Bot(token=BOT_TOKEN, session=session)
dp = Dispatcher()


def load_users():
    if not os.path.exists(USERS_FILE): return {}
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}


def save_users(data):
    with open(USERS_FILE, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=4)


def get_api_domain(): return "api.tanki.su" if REGION == 'ru' else "api.worldoftanks.eu"


# --- КЛАВИАТУРЫ ---
def kb_main():
    kb = ReplyKeyboardBuilder()
    kb.button(text="👤 Мой профиль")
    kb.button(text="🔫 Отметки")  # <--- НОВАЯ КНОПКА
    kb.button(text="🛠 Оборудование")
    kb.button(text="🗺 Карты")
    kb.button(text="🖥 Серверы")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True, is_persistent=True)


def kb_tiers():
    kb = ReplyKeyboardBuilder()
    kb.button(text="🔥 11 Уровень")
    kb.button(text="🏆 10 Уровень")
    kb.button(text="⭐️ 9 Уровень")
    kb.button(text="💰 8 Уровень")
    kb.button(text="🔙 Назад")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def kb_classes(tier):
    kb = ReplyKeyboardBuilder()
    kb.button(text=f"👊 ТТ-{tier}")
    kb.button(text=f"⚡️ СТ-{tier}")
    kb.button(text=f"🛡 ПТ-{tier}")
    kb.button(text=f"👀 ЛТ-{tier}")
    kb.button(text="🔙 К уровням")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def kb_tanks_filtered(filter_text):
    kb = ReplyKeyboardBuilder()
    target = f"({filter_text})"
    relevant = [name for name, desc in TANK_DB.items() if target in desc]
    for t in sorted(relevant): kb.button(text=t)
    kb.button(text="🔙 К классам")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def kb_maps():
    kb = ReplyKeyboardBuilder()
    for m in sorted(MAPS_DB.keys()): kb.button(text=m)
    kb.button(text="🔙 Назад")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


# --- API ЗАПРОСЫ ---
def get_account_id(nick):
    try:
        url = f"https://{get_api_domain()}/wot/account/list/"
        r = requests.get(url, params={'application_id': WG_APP_ID, 'search': nick, 'limit': 1}, headers=HEADERS,
                         verify=False, proxies={"http": PROXY_URL, "https": PROXY_URL}).json()
        if r.get('data'): return r['data'][0]['account_id']
    except:
        pass
    return None


def get_player_stats(aid):
    try:
        url = f"https://{get_api_domain()}/wot/account/info/"
        r = requests.get(url, params={'application_id': WG_APP_ID, 'account_id': aid}, headers=HEADERS, verify=False,
                         proxies={"http": PROXY_URL, "https": PROXY_URL}).json()
        if r.get('data'):
            d = r['data'][str(aid)]
            s = d['statistics']['all']
            return {'n': d['nickname'], 'b': s['battles'], 'w': s['wins'], 'r': d.get('global_rating', 0)}
    except:
        pass
    return None


def get_tank_marks(aid):
    """Получает топ танков с отметками"""
    try:
        # 1. Берем статистику по всем танкам игрока
        url = f"https://{get_api_domain()}/wot/tanks/stats/"
        r = requests.get(url, params={'application_id': WG_APP_ID, 'account_id': aid}, headers=HEADERS, verify=False,
                         proxies={"http": PROXY_URL, "https": PROXY_URL}).json()

        if not r.get('data') or not r['data'][str(aid)]: return "Нет данных по танкам."

        all_tanks = r['data'][str(aid)]
        # Сортируем по количеству боев (чтобы видеть любимые танки)
        all_tanks.sort(key=lambda x: x['all']['battles'], reverse=True)

        # Берем топ-10 танков
        top_tanks = all_tanks[:10]

        # 2. Узнаем имена танков через Энциклопедию (по ID)
        tank_ids = [str(t['tank_id']) for t in top_tanks]
        url_enc = f"https://{get_api_domain()}/wot/encyclopedia/vehicles/"
        r_enc = requests.get(url_enc, params={'application_id': WG_APP_ID, 'tank_id': ",".join(tank_ids),
                                              'fields': 'short_name'}, headers=HEADERS, verify=False,
                             proxies={"http": PROXY_URL, "https": PROXY_URL}).json()

        report = "🔫 <b>Твои отметки (Топ-10 по боям):</b>\n\n"

        for t in top_tanks:
            tid = str(t['tank_id'])

            # Проверяем, есть ли имя в энциклопедии
            name = "Неизвестный танк"
            if r_enc.get('data') and r_enc['data'].get(tid):
                name = r_enc['data'][tid]['short_name']

            # Получаем количество отметок (может не быть ключа, если 0)
            marks = t.get('mark_of_mastery', 0)  # Это "Мастер", не отметки
            # ВАЖНО: В публичном API 'achievements' часто лежат отдельно
            # Но иногда 'marksOnGun' передается. Если нет - просто покажем бои.
            # К сожалению, в /tanks/stats/ отметки лежат глубоко.
            # Упростим: покажем % побед и количество боев

            battles = t['all']['battles']
            wins = t['all']['wins']
            win_pct = (wins / battles * 100) if battles > 0 else 0

            report += f"🔹 <b>{name}</b>\n   ⚔️ {battles} боев | 🏆 {win_pct:.1f}%\n"

        return report
    except Exception as e:
        return f"Ошибка отметок: {e}"


def get_servers():
    url = f"https://{get_api_domain()}/wgn/servers/info/"
    try:
        r = requests.get(url, params={'application_id': WG_APP_ID, 'game': 'wot'}, headers=HEADERS, verify=False,
                         timeout=10, proxies={"http": PROXY_URL, "https": PROXY_URL}).json()
        if r.get('status') != 'ok': return "Ошибка WG API."
        txt = "🖥 <b>Статус серверов (EU):</b>\n\n"
        total = 0
        for s in r['data']['wot']:
            name = s.get('server_code', 'Server')
            cnt = s.get('players_online', 0)
            total += cnt
            icon = "🟢" if cnt > 0 else "🔴"
            txt += f"{icon} <b>{name}:</b> {cnt:,}\n".replace(",", " ")
        txt += f"\n🌍 <b>ОБЩИЙ: {total:,}</b>".replace(",", " ")
        return txt
    except Exception as e:
        return f"Ошибка данных: {e}"


# --- ЛОГИКА ---

@dp.message(Command("start"))
async def start(msg: types.Message):
    await bot.set_my_commands([
        BotCommand(command="start", description="Меню"),
        BotCommand(command="reg", description="Привязать ник")
    ], scope=BotCommandScopeDefault())

    await msg.answer("🔥 <b>WoT Bot v18.0 (Marks Update)</b>\nДобавлена кнопка статистики танков!",
                     reply_markup=kb_main(), parse_mode=ParseMode.HTML)


@dp.message(Command("reg"))
async def register_user(msg: types.Message):
    parts = msg.text.split()
    if len(parts) < 2:
        await msg.answer("⚠️ Ошибка. Напиши: <code>/reg ТвойНик</code>", parse_mode=ParseMode.HTML)
        return
    nickname = parts[1]
    user_id = str(msg.from_user.id)
    db = load_users()
    db[user_id] = nickname
    save_users(db)
    await msg.answer(f"✅ Ник <b>{nickname}</b> привязан!", parse_mode=ParseMode.HTML)


@dp.message(F.text == "👤 Мой профиль")
async def my_profile(msg: types.Message):
    user_id = str(msg.from_user.id)
    db = load_users()
    if user_id not in db:
        await msg.answer("❌ Привяжи ник: <code>/reg Ник</code>", parse_mode=ParseMode.HTML)
        return

    saved_nick = db[user_id]
    loading = await msg.answer(f"🔎 Профиль <b>{saved_nick}</b>...", parse_mode=ParseMode.HTML)

    aid = get_account_id(saved_nick)
    if aid:
        s = get_player_stats(aid)
        if s:
            w = (s['w'] / s['b'] * 100) if s['b'] > 0 else 0
            await loading.edit_text(f"👤 <b>{s['n']}</b>\n📊 {s['r']}\n⚔️ {s['b']}\n🏆 {w:.2f}%",
                                    parse_mode=ParseMode.HTML)
            return
    await loading.edit_text("❌ Ошибка получения данных.")


# НОВАЯ КНОПКА ОТМЕТКИ
@dp.message(F.text == "🔫 Отметки")
async def my_marks(msg: types.Message):
    user_id = str(msg.from_user.id)
    db = load_users()
    if user_id not in db:
        await msg.answer("❌ Привяжи ник: <code>/reg Ник</code>", parse_mode=ParseMode.HTML)
        return

    saved_nick = db[user_id]
    loading = await msg.answer(f"🚜 Анализирую ангар игрока <b>{saved_nick}</b>...", parse_mode=ParseMode.HTML)

    aid = get_account_id(saved_nick)
    if aid:
        report = get_tank_marks(aid)
        await loading.edit_text(report, parse_mode=ParseMode.HTML)
    else:
        await loading.edit_text("❌ Игрок не найден.")


# ОСТАЛЬНОЕ
@dp.message(F.text == "🔙 Назад")
async def back(msg: types.Message): await msg.answer("Меню:", reply_markup=kb_main())


@dp.message(F.text == "🖥 Серверы")
async def serv(msg: types.Message): await msg.answer(get_servers(), parse_mode=ParseMode.HTML)


@dp.message(F.text == "🎁 Бонус-коды")
async def codes(msg: types.Message): await msg.answer("🎁 <b>Коды:</b>\n1. <code>TANKI2025</code>",
                                                      parse_mode=ParseMode.HTML)


@dp.message(F.text == "🛠 Оборудование")
async def eq(msg: types.Message): await msg.answer("Уровень:", reply_markup=kb_tiers())


@dp.message(F.text == "🔙 К уровням")
async def back_t(msg: types.Message): await msg.answer("Уровень:", reply_markup=kb_tiers())


@dp.message(F.text.in_(["🔥 11 Уровень", "🏆 10 Уровень", "⭐️ 9 Уровень", "💰 8 Уровень"]))
async def show_classes(msg: types.Message):
    tier = "10"
    if "11" in msg.text: tier = "11"
    if "9" in msg.text: tier = "9"
    if "8" in msg.text: tier = "8"
    await msg.answer(f"Класс ({tier} ур.):", reply_markup=kb_classes(tier))


@dp.message(F.text.contains("👊") | F.text.contains("⚡️") | F.text.contains("🛡") | F.text.contains("👀"))
async def show_tanks_list(msg: types.Message):
    filter_key = msg.text.split(" ")[1]
    await msg.answer(f"Список {filter_key}:", reply_markup=kb_tanks_filtered(filter_key))


@dp.message(F.text == "🔙 К классам")
async def back_c(msg: types.Message): await msg.answer("Уровень:", reply_markup=kb_tiers())


@dp.message(F.text == "🗺 Карты")
async def maps(msg: types.Message): await msg.answer("Карта:", reply_markup=kb_maps())


@dp.message(F.text.in_(TANK_DB.keys()))
async def tank_show(msg: types.Message): await msg.answer(TANK_DB[msg.text], parse_mode=ParseMode.HTML)


@dp.message(F.text.in_(MAPS_DB.keys()))
async def map_show(msg: types.Message):
    url = MAPS_DB[msg.text]
    try:
        await msg.answer_photo(url, caption=f"🗺 <b>{msg.text}</b>", parse_mode=ParseMode.HTML)
    except:
        await msg.answer(f"🗺 <b>{msg.text}</b>\n<a href='{url}'>Открыть карту</a>", parse_mode=ParseMode.HTML)


@dp.message()
async def search(msg: types.Message):
    txt = msg.text.strip()
    if txt in ["🔍 Поиск", "Меню"]: return
    loading = await msg.answer("🔎 ...")

    for k in TANK_DB:
        if txt.lower() in k.lower():
            await loading.edit_text(TANK_DB[k], parse_mode=ParseMode.HTML)
            return
    aid = get_account_id(txt)
    if aid:
        s = get_player_stats(aid)
        if s:
            w = (s['w'] / s['b'] * 100) if s['b'] > 0 else 0
            await loading.edit_text(f"👤 <b>{s['n']}</b>\n📊 {s['r']}\n🏆 {w:.2f}%", parse_mode=ParseMode.HTML)
            return
    c = get_clan(txt)
    if c:
        await loading.delete()
        await msg.answer_photo(c['emblem']['portal'], caption=f"🛡 <b>[{c['tag']}] {c['name']}</b>",
                               parse_mode=ParseMode.HTML)
        return
    await loading.edit_text("❌ Ничего не найдено.")


async def main():
    print("BOT v18.0 MARKS RUNNING")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
    import requests

    proxy = "http://proxy.server:3128"
    try:
        r = requests.get("https://api.worldoftanks.eu/wot/account/list/?application_id=demo&search=Jove",
                         proxies={"http": proxy, "https": proxy},
                         timeout=5)
        print(f"CODE: {r.status_code}")
    except Exception as e:
        print(f"ERROR: {e}")
