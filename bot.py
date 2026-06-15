import asyncio
import random
import string
import os
import aiosqlite
import qrcode
import wikipedia
from gtts import gTTS
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject
from aiogram.types import FSInputFile

# Настройка языка для Википедии
wikipedia.set_lang("ru")

BOT_TOKEN = "8816734888:AAG6gApnQMqt01gfkzM-O1-L43cFnBytdgk"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Инициализация базы данных
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

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    welcome_text = (
        "Привет! Я твой мощный Бот-Швейцарский нож 🛠\n\n"
        "<b>🔐 Управление паролями:</b>\n"
        "/password — Сгенерировать пароль\n"
        "/savepass [сервис] [пароль] — Сохранить пароль\n"
        "/mypass — Мои пароли\n"
        "/delpass [сервис] — Удалить пароль\n\n"
        "<b>🧰 Полезные утилиты:</b>\n"
        "/voice [текст] — Озвучить текст\n"
        "/qr [текст/ссылка] — Создать QR-код\n"
        "/wiki [слово] — Поиск в Википедии\n"
        "/coin — Бросить монетку (Орёл/Решка)\n\n"
        "🚀 <b>Кстати, зацени моего второго бота:</b> @guga23_bot"
    )
    await message.answer(welcome_text, parse_mode="HTML")

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

# --- БЛОК УТИЛИТ ---

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
        await message.answer("⚠️ Что ищем? Напиши, например: <code>/wiki Космос</code>", parse_mode="HTML")
        return
    
    msg = await message.answer("🔍 Ищу в Википедии...")
    try:
        # Берем первые 3 предложения из статьи
        result = wikipedia.summary(command.args, sentences=3)
        await msg.edit_text(f"📖 <b>{command.args.capitalize()}</b>\n\n{result}", parse_mode="HTML")
    except wikipedia.exceptions.DisambiguationError:
        await msg.edit_text("🤷‍♂️ Запрос слишком общий, уточни его (например, не 'Яблоко', а 'Яблоко (плод)').")
    except wikipedia.exceptions.PageError:
        await msg.edit_text("😔 По твоему запросу ничего не найдено в Википедии.")
    except Exception:
        await msg.edit_text("❌ Ошибка при поиске.")

@dp.message(Command("coin"))
async def cmd_coin(message: types.Message):
    result = random.choice(["Орёл 🦅", "Решка 🪙"])
    await message.answer(f"Подбрасываем монетку...\n\nВыпало: <b>{result}</b>", parse_mode="HTML")

async def main():
    await init_db()
    print("Бот успешно запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
