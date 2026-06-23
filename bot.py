import logging
import uuid
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from yookassa import Configuration, Payment
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
YUKASSA_SHOP_ID = os.getenv("YUKASSA_SHOP_ID")
YUKASSA_SECRET_KEY = os.getenv("YUKASSA_SECRET_KEY")

Configuration.account_id = YUKASSA_SHOP_ID
Configuration.secret_key = YUKASSA_SECRET_KEY

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

PRODUCTS = {
    "resume": {"name": "Гайд по резюме", "price": "390.00", "file": "resume.pdf"},
    "interview": {"name": "Гайд по собеседованию", "price": "390.00", "file": "interview.pdf"},
    "bundle": {"name": "Оба гайда", "price": "749.00", "file": None},
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
        photo=open("/data/welcome.png", "rb"),
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

    bot_info = await bot.get_me()
    payment = Payment.create({
        "amount": {"value": product["price"], "currency": "RUB"},
        "confirmation": {
            "type": "redirect",
            "return_url": f"https://t.me/{bot_info.username}"
        },
        "capture": True,
        "description": product["name"],
        "metadata": {
            "user_id": str(callback.from_user.id),
            "product_key": product_key
        }
    }, str(uuid.uuid4()))

    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("💳 Оплатить", url=payment.confirmation.confirmation_url),
        InlineKeyboardButton("✅ Я оплатил — получить гайд", callback_data=f"check_{payment.id}_{product_key}"),
        InlineKeyboardButton("⬅️ Назад", callback_data="back")
    )
    await callback.message.answer(
        f"*{product['name']}*\n\n"
        f"Сумма: *{product['price'].replace('.00', '')} ₽*\n\n"
        "1️⃣ Нажми «Оплатить» и заверши оплату\n"
        "2️⃣ Вернись сюда и нажми «Я оплатил»\n"
        "3️⃣ Получи гайд автоматически 📥",
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
        await callback.message.answer("✅ Оплата прошла! Отправляю гайд...")

        if product_key == "bundle":
            await bot.send_document(
                callback.from_user.id,
                open("/data/resume.pdf", "rb"),
                caption="📄 Гайд «Как написать резюме, которое не выбросят за 10 секунд»"
            )
            await bot.send_document(
                callback.from_user.id,
                open("/data/interview.pdf", "rb"),
                caption="🎯 Гайд «Как пройти собеседование и получить оффер»"
            )
        else:
            await bot.send_document(
                callback.from_user.id,
                open(f"/data/{product['file']}", "rb"),
                caption=f"📎 {product['name']}"
            )

        await callback.message.answer(
            "🎉 Спасибо за покупку!\n\n"
            "Если гайд был полезен — буду рад отзыву.\n"
            "Поделись с другом, кому это может помочь 🙌\n\n"
            "Напиши /start чтобы вернуться в главное меню."
        )
    elif payment.status == "pending":
        await callback.message.answer(
            "⏳ Оплата ещё не поступила.\n"
            "Завершите оплату и нажмите кнопку снова."
        )
    else:
        await callback.message.answer(
            "❌ Что-то пошло не так с оплатой.\n"
            "Попробуйте ещё раз или напишите /start"
        )
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data == "back")
async def back(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.answer()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
