import asyncio
import random
import string
import os
import aiosqlite
from gtts import gTTS
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject
from aiogram.types import FSInputFile

# Вставь сюда токен, который выдаст @BotFather в Telegram
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
        "Привет! Я твой личный Бот-Помощник 🛠\n\n"
        "<b>Мои функции:</b>\n"
        "🔑 /password — Сгенерировать надежный пароль\n"
        "💾 /savepass [сервис] [пароль] — Сохранить пароль (например: <i>/savepass VK 12345</i>)\n"
        "📂 /mypass — Посмотреть все сохраненные пароли\n"
        "🎙 /voice [текст] — Озвучить текст голосовым сообщением\n\n"
        "🚀 <b>Зацени моего второго крутого бота:</b> @guga23_bot"
    )
    await message.answer(welcome_text, parse_mode="HTML")

@dp.message(Command("password"))
async def cmd_password(message: types.Message):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    pwd = ''.join(random.choice(chars) for _ in range(12))
    await message.answer(
        f"🔐 Твой новый пароль: <code>{pwd}</code>\n"
        "<i>(нажми, чтобы скопировать. Чтобы сохранить, используй команду /savepass)</i>", 
        parse_mode="HTML"
    )

@dp.message(Command("savepass"))
async def cmd_savepass(message: types.Message, command: CommandObject):
    if not command.args or len(command.args.split()) < 2:
        await message.answer("⚠️ Использование: <code>/savepass Название_сервиса Пароль</code>", parse_mode="HTML")
        return
    
    args = command.args.split()
    service = args[0]
    password = args[1]
    
    async with aiosqlite.connect('passwords.db') as db:
        await db.execute('INSERT INTO passwords (user_id, service, password) VALUES (?, ?, ?)', 
                         (message.from_user.id, service, password))
        await db.commit()
        
    await message.answer(f"✅ Пароль для <b>{service}</b> успешно сохранен!", parse_mode="HTML")

@dp.message(Command("mypass"))
async def cmd_mypass(message: types.Message):
    async with aiosqlite.connect('passwords.db') as db:
        async with db.execute('SELECT service, password FROM passwords WHERE user_id = ?', (message.from_user.id,)) as cursor:
            rows = await cursor.fetchall()
            
    if not rows:
        await message.answer("У тебя пока нет сохраненных паролей. Используй /savepass.")
        return
        
    text = "📂 <b>Твои сохраненные пароли:</b>\n\n"
    for service, password in rows:
        text += f"▪️ <b>{service}</b>: <code>{password}</code>\n"
        
    await message.answer(text, parse_mode="HTML")

@dp.message(Command("voice"))
async def cmd_voice(message: types.Message, command: CommandObject):
    if not command.args:
        await message.answer("⚠️ Напиши текст после команды. Например: <code>/voice Привет, как дела?</code>", parse_mode="HTML")
        return
    
    # Отправляем сообщение "Генерирую..." чтобы пользователь не скучал
    msg = await message.answer("⏳ Генерирую голосовое, подожди секунду...")
    
    try:
        # Генерация аудио
        tts = gTTS(text=command.args, lang='ru')
        filename = f"voice_{message.from_user.id}.ogg"
        tts.save(filename)
        
        # Отправка аудио
        voice = FSInputFile(filename)
        await message.answer_voice(voice)
        
        # Удаляем временный файл и сообщение "Генерирую..."
        os.remove(filename)
        await msg.delete()
        
    except Exception as e:
        await msg.edit_text("❌ Произошла ошибка при генерации аудио.")

async def main():
    await init_db() # Запускаем базу данных перед стартом
    print("Бот успешно запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
