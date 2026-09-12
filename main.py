import asyncio
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiohttp import web

# --- ВАШИ ДАННЫЕ ПРОПИСАНЫ ---
BOT_TOKEN = "8612937803:AAHY-mx1Xm7eX7BbdaqjJ4olYMrNErOm6TE"
ADMIN_ID = 6462524616  
DEV_CHAT_LINK = "https://t.me"

# --- ШАБЛОН АНКЕТЫ ---
ANKETA_TEMPLATE = (
    "Привет! Чтобы подать заявку в команду мессенджера Pulse, "
    "скопируй этот шаблон, заполни его и отправь ответным сообщением:\n\n"
    "1. Ваше имя / Никнейм:\n"
    "2. Ваш основной стек и опыт в программировании:\n"
    "3. Опыт работы с ИИ-инструментами (вайбкодинг):\n"
    "4. Сколько времени в неделю готовы уделять проекту Pulse?:\n"
    "5. Почему вам интересен этот проект?:"
)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 1. Перехват заявки в группу -> Автоотклонение + Отправка анкеты в ЛС
@dp.chat_join_request()
async def handle_join_request(update: types.ChatJoinRequest):
    try:
        await update.decline()
        await bot.send_message(chat_id=update.from_user.id, text=ANKETA_TEMPLATE)
    except Exception as e:
        print(f"Ошибка при обработке заявки: {e}")

# 2. Получение заполненной анкеты в ЛС бота -> Пересылка админу с кнопками
@dp.message(F.chat.type == "private")
async def handle_anketa(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        return
        
    admin_text = (
        f"📋 **Новая заявка от кандидата!**\n"
        f"Имя: {message.from_user.full_name}\n"
        f"Юзернейм: @{message.from_user.username if message.from_user.username else 'отсутствует'}\n"
        f"ID соискателя: `{message.from_user.id}`\n\n"
        f"**Текст анкеты:**\n{message.text}"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🟢 Принять", callback_data=f"accept_{message.from_user.id}"),
            InlineKeyboardButton(text="🔴 Отклонить", callback_data=f"decline_{message.from_user.id}")
        ]
    ])
    
    await bot.send_message(chat_id=ADMIN_ID, text=admin_text, reply_markup=keyboard, parse_mode="Markdown")
    await message.answer("Спасибо! Ваша анкету отправлена руководителю на рассмотрение.")

# 3. Обработка нажатия кнопок [Принять] / [Отклонить] в вашем ЛС
@dp.callback_query(F.data.startswith("accept_") | F.data.startswith("decline_"))
async def process_moderation(callback: types.CallbackQuery):
    action, user_id = callback.data.split("_")
    user_id = int(user_id)
    
    if action == "accept":
        await bot.send_message(
            chat_id=user_id,
            text=f"🎉 Поздравляем! Ваша заявка одобрена. Добро пожаловать в команду Pulse.\n"
                 f"Вот ваша постоянная ссылка на чат разработчиков: {DEV_CHAT_LINK}"
        )
        await callback.message.edit_text(callback.message.text + "\n\n✅ **Кандидат принят, ссылка отправлена.**")
    
    elif action == "decline":
        await bot.send_message(
            chat_id=user_id,
            text="Спасибо за отклик! К сожалению, на данный момент мы не готовы пригласить вас в команду разработки. Желаем удачи!"
        )
        await callback.message.edit_text(callback.message.text + "\n\n❌ **Заявка отклонена.**")
        
    await callback.answer()

# --- МИНИ-СЕРВЕР ДЛЯ ОБМАНА РЕНДЕРА (ПОРТ) ---
async def handle_web(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_web)
    runner = web.AppRunner(app)
    await runner.setup()
    # Читаем порт, который требует Render
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Веб-сервер успешно запущен на порту {port}")

async def main():
    # Запускаем фоновый веб-сервер для проверки портов Render
    await start_web_server()
    # Запускаем опрос Telegram
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
