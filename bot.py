import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from yookassa import Configuration, Payment
import uuid
import os

# Настройки
BOT_TOKEN = os.getenv("BOT_TOKEN")
YUKASSA_SHOP_ID = os.getenv("YUKASSA_SHOP_ID")
YUKASSA_SECRET_KEY = os.getenv("YUKASSA_SECRET_KEY")

Configuration.account_id = YUKASSA_SHOP_ID
Configuration.secret_key = YUKASSA_SECRET_KEY

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

PRODUCTS = {
    "resume": {
        "name": "Гайд «Как написать резюме, которое не выбросят за 10 секунд»",
        "price": 590,
        "file": "resume.pdf"
    },
    "interview": {
        "name": "Гайд «Как пройти собеседование и получить оффер»",
        "price": 590,
        "file": "interview.pdf"
    },
    "bundle": {
        "name": "Оба гайда со скидкой",
        "price": 990,
        "file": None
    }
}

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
    product_key = callback.data.replace("buy_", "")
    product = PRODUCTS[product_key]

    payment = Payment.create({
        "amount": {
            "value": str(product["price"]) + ".00",
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me/" + (await bot.get_me()).username
        },
        "capture": True,
        "description": product["name"],
        "metadata": {
            "user_id": str(callback.from_user.id),
            "product_key": product_key
        }
    }, uuid.uuid4())

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("💳 Оплатить", url=payment.confirmation.confirmation_url))
    kb.add(InlineKeyboardButton("✅ Я оплатил — проверить", callback_data=f"check_{payment.id}_{product_key}"))

    await callback.message.answer(
        f"*{product['name']}*\n\n"
        f"Сумма: *{product['price']} ₽*\n\n"
        "Нажми «Оплатить», заверши оплату и вернись сюда. "
        "Затем нажми «Я оплатил — проверить» и получи гайд.",
        reply_markup=kb,
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("check_"))
async def check_payment(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    payment_id = parts[1]
    product_key = parts[2]

    payment = Payment.find_one(payment_id)

    if payment.status == "succeeded":
        product = PRODUCTS[product_key]
        await
