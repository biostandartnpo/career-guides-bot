import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("📄 Гайд по резюме — 590 ₽", callback_data="buy_resume"),
        InlineKeyboardButton("🎯 Гайд по собеседованию — 590 ₽", callback_data="buy_interview"),
        InlineKeyboardButton("🔥 Оба гайда — 990 ₽ (скидка 190 ₽)", callback_data="buy_bundle"),
    )
    await message.answer(
        "👋 Привет! Я помогу тебе найти работу мечты.\n\n"
        "У меня два практических гайда:\n\n"
        "📄 *Как написать резюме, которое не выбросят за 10 секунд*\n"
        "— структура, примеры, частые ошибки, готовый шаблон\n\n"
        "🎯 *Как пройти собеседование и получить оффер*\n"
        "— подготовка, сложные вопросы, переговоры о зарплате\n\n"
        "Выбирай 👇",
        reply_markup=kb,
        parse_mode="Markdown"
    )

@dp.callback_query_handler(lambda c: c.data.startswith("buy_"))
async def buy(callback: types.CallbackQuery):
    prices = {
        "buy_resume": ("Гайд по резюме", "590"),
        "buy_interview": ("Гайд по собеседованию", "590"),
        "buy_bundle": ("Оба гайда", "990"),
    }
    name, price = prices[callback.data]
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("💳 Оплатить", callback_data="pay_soon"))
    kb.add(InlineKeyboardButton("⬅️ Назад", callback_data="back"))
    await callback.message.answer(
        f"*{name}*\n\n"
        f"Сумма: *{price} ₽*\n\n"
        "После оплаты гайд придёт сюда автоматически.",
        reply_markup=kb,
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data == "pay_soon")
async def pay_soon(callback: types.CallbackQuery):
    await callback.message.answer("⏳ Оплата скоро будет доступна. Следите за обновлениями!")
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data == "back")
async def back(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.answer()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
