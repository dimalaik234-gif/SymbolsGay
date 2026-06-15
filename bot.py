import asyncio
import random
import string
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject

# Вставь сюда токен, который выдаст @BotFather в Telegram
BOT_TOKEN = "8816734888:AAG6gApnQMqt01gfkzM-O1-L43cFnBytdgk"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    welcome_text = (
        "Привет! Я <b>Бот-Текстовик</b> ✍️\n\n"
        "Вот что я умею:\n"
        "1️⃣ Отправь мне любое сообщение, и я посчитаю в нем слова и символы.\n"
        "2️⃣ Напиши <code>/reverse твой текст</code>, чтобы перевернуть его задом наперед.\n"
        "3️⃣ Напиши <code>/password</code>, чтобы сгенерировать надежный пароль."
    )
    await message.answer(welcome_text, parse_mode="HTML")

@dp.message(Command("password"))
async def cmd_password(message: types.Message):
    # Генерируем пароль из 12 символов (буквы, цифры и спецсимволы)
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    pwd = ''.join(random.choice(chars) for _ in range(12))
    await message.answer(f"🔐 Твой новый пароль: <code>{pwd}</code>\n<i>(нажми на пароль, чтобы скопировать)</i>", parse_mode="HTML")

@dp.message(Command("reverse"))
async def cmd_reverse(message: types.Message, command: CommandObject):
    # Проверяем, передал ли пользователь текст после команды
    if command.args:
        reversed_text = command.args[::-1]
        await message.answer(reversed_text)
    else:
        await message.answer("После команды нужно написать текст. Например: <code>/reverse Привет</code>", parse_mode="HTML")

# Обработчик обычных текстовых сообщений (считает статистику текста)
@dp.message(F.text)
async def count_text(message: types.Message):
    text = message.text
    char_count = len(text)
    word_count = len(text.split())
    
    response = (
        "📊 <b>Анализ текста:</b>\n"
        f"Символов (с пробелами): {char_count}\n"
        f"Слов: {word_count}"
    )
    await message.reply(response, parse_mode="HTML")

async def main():
    print("Бот-утилита успешно запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
