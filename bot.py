import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from aiogram.utils import executor
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

PRODUCTS = {
    "resume": {"name": "Гайд по резюме", "price": "390"},
    "interview": {"name": "Гайд по собеседованию", "price": "390"},
    "bundle": {"name": "Оба гайда", "price": "749"},
}

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("📄 Гайд по резюме — 390 ₽", callback_data="buy_resume"),
        InlineKeyboardButton("🎯 Гайд по собеседованию — 390 ₽", callback_data="buy_interview"),
        InlineKeyboardButton("🔥 Оба гайда — 749 ₽ (скидка 31 ₽)", callback_data="buy_bundle"),
    )
    await bot.send_photo(
        message.chat.id,
        photo=open("welcome.png", "rb"),
        caption=(
            "👋 Привет! Я бот *КарьераПро* — твой помощник в карьере.\n\n"
            "У меня два практических гайда:\n\n"
            "📄 *Как написать резюме, которое не выбросят за 10 секунд*\n"
            "— структура, примеры, частые ошибки, готовый шаблон\n\n"
            "🎯 *Как пройти собеседование и получить оффер*\n"
            "— подготовка, сложные вопросы, переговоры о зарплате\n\n"
            "Выбирай гайд и прокачивай карьеру! 👇"
        ),
        reply_markup=kb,
        parse_mode="Markdown"
    )

@dp.callback_query_handler(lambda c: c.data.startswith("buy_"))
async def buy(callback: types.CallbackQuery):
    product_key = callback.data.replace("buy_", "")
    product = PRODUCTS[product_key]
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("💳 Оплатить", callback_data="pay_soon"),
        InlineKeyboardButton("⬅️ Назад", callback_data="back")
    )
    await callback.message.answer(
        f"*{product['name']}*\n\n"
        f"Сумма: *{product['price']} ₽*\n\n"
        "После оплаты гайд придёт сюда автоматически.",
        reply_markup=kb,
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data == "pay_soon")
async def pay_soon(callback: types.CallbackQuery):
    await callback.message.answer(
        "⏳ Оплата скоро будет доступна. Следите за обновлениями!\n\n"
        "Напишите /start чтобы вернуться в главное меню."
    )
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data == "back")
async def back(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.answer()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
