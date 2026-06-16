import asyncio
import random
import string
import os
import re
import aiosqlite
import qrcode
import aiohttp
from gtts import gTTS
from deep_translator import GoogleTranslator
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject
from aiogram.types import FSInputFile

# Вставь сюда токен, который выдаст @BotFather
BOT_TOKEN = "8816734888:AAG6gApnQMqt01gfkzM-O1-L43cFnBytdgk"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- БАЗА ПЕСЕН ДЛЯ БОТА ---
SONGS = {
    "1": {
        "title": "Кино — Звезда по имени Солнце",
        "lyrics": [
            "Белый снег, серый лёд,",
            "На растрескавшейся земле.",
            "Одеялом лоскутным на ней —",
            "Город в дорожной петле.",
            "А над городом плывут облака,",
            "Закрывая небесный свет.",
            "А над городом — жёлтый дым,",
            "Городу две тысячи лет,",
            "Прожитых под светом Звезды",
            "По имени Солнце..."
        ]
    },
    "2": {
        "title": "Король и Шут — Кукла колдуна",
        "lyrics": [
            "Тёмный, мрачный коридор,",
            "Я на цыпочках, как вор,",
            "Пробираюсь, чуть дыша,",
            "Чтобы не спугнуть",
            "Тех, кто спит уже давно,",
            "Те, кому не всё равно,",
            "В чью я комнату тайком",
            "Желаю заглянуть...",
            "Всё происходит как во сне,",
            "А моя душа не на месте,",
            "Я брожу в тишине..."
        ]
    },
    "3": {
        "title": "Сектор Газа — Лирика",
        "lyrics": [
            "Сигарета мелькает во тьме...",
            "Ветер пепел в лицо швырнул мне.",
            "И обугленный фильтр на пальцах мне оставил ожог.",
            "Скрипнув дверью, как серые кошки,",
            "Ночь покорно улеглась на окошке,",
            "Привидением чёрным из ниоткуда появился сверчок."
        ]
    }
}

# --- ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ ---
async def init_db():
    async with aiosqlite.connect('passwords.db') as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS passwords (
                user_id INTEGER, 
                service TEXT, 
                password TEXT
            )
        ''')
        await db.commit()

# --- ПРИВЕТСТВИЕ И МЕНЮ ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    welcome_text = (
        "Привет! Я твой супер-Бот 🛠\n\n"
        "<b>🔐 Управление паролями:</b>\n"
        "/password — Сгенерировать пароль\n"
        "/savepass [сервис] [пароль] — Сохранить пароль\n"
        "/mypass — Мои пароли\n"
        "/delpass [сервис] — Удалить пароль\n\n"
        "<b>🧰 Полезные утилиты:</b>\n"
        "/voice [текст] — Озвучить текст\n"
        "/qr [текст/ссылка] — Создать QR-код\n"
        "/wiki [слово] — Поиск в Википедии\n"
        "/calc [выражение] — Калькулятор (например: 2+2*2)\n"
        "/weather [город] — Узнать погоду\n"
        "/tr [текст] — Переводчик (RU ↔ EN)\n"
        "/short [ссылка] — Сократить ссылку\n"
        "/remind [минуты] [текст] — Поставить напоминание\n\n"
        "<b>🎲 Развлечения:</b>\n"
        "/coin — Бросить монетку (Орёл/Решка)\n"
        "/roll [число] — Случайное число до N\n"
        "/sing — Спеть песню (Караоке)\n\n"
        "🚀 <b>Кстати, зацени моего второго бота:</b> @guga23_bot"
    )
    await message.answer(welcome_text, parse_mode="HTML")

# --- БЛОК КАРАОКЕ (ПЕСНИ) ---
@dp.message(Command("sing"))
async def cmd_sing(message: types.Message, command: CommandObject):
    if not command.args or command.args not in SONGS:
        # Если пользователь не выбрал песню, показываем меню
        text = "🎤 <b>Караоке-бар бота!</b>\nВыбери песню и напиши её номер (например: <code>/sing 1</code>):\n\n"
        for key, song in SONGS.items():
            text += f"<b>{key}.</b> {song['title']}\n"
        await message.answer(text, parse_mode="HTML")
        return

    # Если песня выбрана, начинаем петь
    song = SONGS[command.args]
    await message.answer(f"🎶 Начинаю петь: <b>{song['title']}</b>", parse_mode="HTML")
    await asyncio.sleep(1.5) # Пауза перед началом

    # Разбиваем текст на куплеты (по 4 строчки) и отправляем с задержкой
    chunk_size = 4
    lines = song['lyrics']
    for i in range(0, len(lines), chunk_size):
        chunk = "\n".join(lines[i:i+chunk_size])
        await message.answer(f"🎵 <i>{chunk}</i>", parse_mode="HTML")
        await asyncio.sleep(3) # Пауза между куплетами для имитации пения
    
    await asyncio.sleep(1)
    await message.answer("👏 <i>*Звучат аплодисменты*</i>", parse_mode="HTML")

# --- БЛОК УПРАВЛЕНИЯ ПАРОЛЯМИ ---
@dp.message(Command("password"))
async def cmd_password(message: types.Message):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    pwd = ''.join(random.choice(chars) for _ in range(12))
    await message.answer(f"🔐 Твой пароль: <code>{pwd}</code>", parse_mode="HTML")

@dp.message(Command("savepass"))
async def cmd_savepass(message: types.Message, command: CommandObject):
    if not command.args or len(command.args.split()) < 2:
        await message.answer("⚠️ Пиши так: <code>/savepass VK 12345</code>", parse_mode="HTML")
        return
    args = command.args.split()
    service, password = args[0], args[1]
    
    async with aiosqlite.connect('passwords.db') as db:
        await db.execute('INSERT INTO passwords (user_id, service, password) VALUES (?, ?, ?)', 
                         (message.from_user.id, service, password))
        await db.commit()
    await message.answer(f"✅ Пароль для <b>{service}</b> сохранен!", parse_mode="HTML")

@dp.message(Command("mypass"))
async def cmd_mypass(message: types.Message):
    async with aiosqlite.connect('passwords.db') as db:
        async with db.execute('SELECT service, password FROM passwords WHERE user_id = ?', (message.from_user.id,)) as cursor:
            rows = await cursor.fetchall()
            
    if not rows:
        await message.answer("У тебя пока нет сохраненных паролей.")
        return
        
    text = "📂 <b>Твои пароли:</b>\n\n"
    for service, password in rows:
        text += f"▪️ <b>{service}</b>: <code>{password}</code>\n"
    await message.answer(text, parse_mode="HTML")

@dp.message(Command("delpass"))
async def cmd_delpass(message: types.Message, command: CommandObject):
    if not command.args:
        await message.answer("⚠️ Напиши название сервиса: <code>/delpass VK</code>", parse_mode="HTML")
        return
    
    service = command.args.strip()
    async with aiosqlite.connect('passwords.db') as db:
        await db.execute('DELETE FROM passwords WHERE user_id = ? AND service = ?', (message.from_user.id, service))
        await db.commit()
    await message.answer(f"🗑 Пароль для <b>{service}</b> удален (если он был в базе).", parse_mode="HTML")

# --- БЛОК СТАРЫХ УТИЛИТ ---
@dp.message(Command("voice"))
async def cmd_voice(message: types.Message, command: CommandObject):
    if not command.args:
        await message.answer("⚠️ Напиши текст после команды.")
        return
    
    msg = await message.answer("⏳ Генерирую...")
    try:
        tts = gTTS(text=command.args, lang='ru')
        filename = f"voice_{message.from_user.id}.ogg"
        tts.save(filename)
        await message.answer_voice(FSInputFile(filename))
        os.remove(filename)
        await msg.delete()
    except Exception:
        await msg.edit_text("❌ Ошибка генерации.")

@dp.message(Command("qr"))
async def cmd_qr(message: types.Message, command: CommandObject):
    if not command.args:
        await message.answer("⚠️ Напиши текст или ссылку для QR-кода.")
        return
    
    msg = await message.answer("⏳ Рисую QR-код...")
    try:
        img = qrcode.make(command.args)
        filename = f"qr_{message.from_user.id}.png"
        img.save(filename)
        await message.answer_photo(FSInputFile(filename), caption="Вот твой QR-код! ⬛️⬜️")
        os.remove(filename)
        await msg.delete()
    except Exception:
        await msg.edit_text("❌ Ошибка создания QR-кода.")

@dp.message(Command("wiki"))
async def cmd_wiki(message: types.Message, command: CommandObject):
    if not command.args:
        await message.answer("⚠️ Что ищем? Напиши: <code>/wiki Космос</code>", parse_mode="HTML")
        return
    
    msg = await message.answer("🔍 Ищу в Википедии...")
    url = "https://ru.wikipedia.org/w/api.php"
    params = {"action": "query", "format": "json", "prop": "extracts", "exsentences": "3", "exlimit": "1", "explaintext": "1", "titles": command.args}
    headers = {"User-Agent": "MyTelegramBot/1.0 (https://t.me/guga23_bot)"}
    
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
                
        pages = data.get("query", {}).get("pages", {})
        for page_id, page_data in pages.items():
            if page_id == "-1":
                await msg.edit_text("😔 Ничего не найдено.")
                return
            extract = page_data.get("extract", "").strip()
            title = page_data.get("title", "")
            if not extract:
                await msg.edit_text(f"😔 Статья <b>{title}</b> найдена, но текста нет.", parse_mode="HTML")
                return
            await msg.edit_text(f"📖 <b>{title}</b>\n\n{extract}", parse_mode="HTML")
            return
    except Exception as e:
        await msg.edit_text(f"❌ Ошибка: {e}")

@dp.message(Command("coin"))
async def cmd_coin(message: types.Message):
    result = random.choice(["Орёл 🦅", "Решка 🪙"])
    await message.answer(f"Подбрасываем монетку...\n\nВыпало: <b>{result}</b>", parse_mode="HTML")

@dp.message(Command("calc"))
async def cmd_calc(message: types.Message, command: CommandObject):
    if not command.args:
        await message.answer("⚠️ Введи выражение. Например: <code>/calc 25*4-10</code>", parse_mode="HTML")
        return
    
    async with aiohttp.ClientSession() as session:
        async with session.get("http://api.mathjs.org/v4/", params={"expr": command.args}) as resp:
            if resp.status == 200:
                result = await resp.text()
                await message.answer(f"🧮 <b>Ответ:</b> {result}", parse_mode="HTML")
            else:
                await message.answer("❌ Ошибка. Проверь правильность математического выражения.")

@dp.message(Command("weather"))
async def cmd_weather(message: types.Message, command: CommandObject):
    if not command.args:
        await message.answer("⚠️ Напиши город. Например: <code>/weather Москва</code>", parse_mode="HTML")
        return
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://wttr.in/{command.args}?format=3") as resp:
            if resp.status == 200:
                result = await resp.text()
                await message.answer(f"☁️ <b>Погода:</b>\n{result.strip()}", parse_mode="HTML")
            else:
                await message.answer("❌ Город не найден.")

@dp.message(Command("tr"))
async def cmd_tr(message: types.Message, command: CommandObject):
    if not command.args:
        await message.answer("⚠️ Напиши текст для перевода. Например: <code>/tr Hello world</code>", parse_mode="HTML")
        return
    
    try:
        if re.search('[а-яА-ЯёЁ]', command.args):
            translated = GoogleTranslator(source='auto', target='en').translate(command.args)
        else:
            translated = GoogleTranslator(source='auto', target='ru').translate(command.args)
            
        await message.answer(f"🌐 <b>Перевод:</b>\n{translated}", parse_mode="HTML")
    except Exception:
        await message.answer("❌ Произошла ошибка при переводе.")

@dp.message(Command("short"))
async def cmd_short(message: types.Message, command: CommandObject):
    if not command.args:
        await message.answer("⚠️ Отправь ссылку. Например: <code>/short https://очень-длинная-ссылка.com</code>", parse_mode="HTML")
        return
    
    msg = await message.answer("⏳ Сокращаю...")
    url = f"https://tinyurl.com/api-create.php?url={command.args}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    short_url = await resp.text()
                    await msg.edit_text(f"🔗 <b>Короткая ссылка:</b>\n{short_url}", parse_mode="HTML")
                else:
                    await msg.edit_text("❌ Ошибка. Возможно, ссылка недействительна.")
    except Exception:
        await msg.edit_text("❌ Ошибка при соединении с сервером.")

@dp.message(Command("roll"))
async def cmd_roll(message: types.Message, command: CommandObject):
    limit = 100
    if command.args and command.args.isdigit():
        limit = int(command.args)
        if limit < 2:
            limit = 100
            
    result = random.randint(1, limit)
    await message.answer(f"🎲 Выпало число: <b>{result}</b> (из {limit})", parse_mode="HTML")

@dp.message(Command("remind"))
async def cmd_remind(message: types.Message, command: CommandObject):
    if not command.args or len(command.args.split()) < 2:
        await message.answer("⚠️ Пиши так: <code>/remind 5 Выключить духовку</code> (где 5 - это минуты)", parse_mode="HTML")
        return
    
    args = command.args.split(" ", 1)
    if not args[0].isdigit():
        await message.answer("⚠️ Первым аргументом обязательно должно быть число (количество минут).")
        return
    
    minutes = int(args[0])
    text = args[1]
    
    if minutes > 1440:
        await message.answer("⚠️ Максимальное время напоминания — 24 часа (1440 минут).")
        return

    await message.answer(f"✅ Напоминание установлено! Я напишу тебе через {minutes} минут.")
    await asyncio.sleep(minutes * 60)
    await message.reply(f"⏰ <b>НАПОМИНАНИЕ:</b>\n{text}", parse_mode="HTML")

async def main():
    await init_db()
    print("Бот успешно запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
