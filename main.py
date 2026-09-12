import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# --- ВАШИ ДАННЫЕ АВТОМАТИЧЕСКИ ПРОПИСАНЫ ---
BOT_TOKEN = "8612937803:AAHY-mx1Xm7eX7BbdaqjJ4olYMrNErOm6TE"
ADMIN_ID = 6462524616  
DEV_CHAT_LINK = "https://t.me/+18aZ2iVLUOU4Mjhi"

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
        # Автоматически отклоняем заявку в группу, чтобы очистить списки чатов
        await update.decline()
        
        # Сразу пишем пользователю в ЛС и выдаем шаблон анкеты
        await bot.send_message(chat_id=update.from_user.id, text=ANKETA_TEMPLATE)
    except Exception as e:
        print(f"Ошибка при обработке заявки: {e}")

# 2. Получение заполненной анкеты в ЛС бота -> Пересылка админу с кнопками
@dp.message(F.chat.type == "private")
async def handle_anketa(message: types.Message):
    # Если пишет сам админ, игнорируем, чтобы не зацикливать
    if message.from_user.id == ADMIN_ID:
        return
        
    # Формируем текст для админа
    admin_text = (
        f"📋 **Новая заявка от кандидата!**\n"
        f"Имя: {message.from_user.full_name}\n"
        f"Юзернейм: @{message.from_user.username if message.from_user.username else 'отсутствует'}\n"
        f"ID соискателя: `{message.from_user.id}`\n\n"
        f"**Текст анкеты:**\n{message.text}"
    )
    
    # Создаем интерактивные кнопки модерации для админа
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🟢 Принять", callback_data=f"accept_{message.from_user.id}"),
            InlineKeyboardButton(text="🔴 Отклонить", callback_data=f"decline_{message.from_user.id}")
        ]
    ])
    
    # Отправляем анкету вам в ЛС
    await bot.send_message(chat_id=ADMIN_ID, text=admin_text, reply_markup=keyboard, parse_mode="Markdown")
    # Подтверждение кандидату
    await message.answer("Спасибо! Ваша анкета отправлена руководителю на рассмотрение.")

# 3. Обработка нажатия кнопок [Принять] / [Отклонить] в вашем ЛС
@dp.callback_query(F.data.startswith("accept_") | F.data.startswith("decline_"))
async def process_moderation(callback: types.CallbackQuery):
    action, user_id = callback.data.split("_")
    user_id = int(user_id)
    
    if action == "accept":
        # Отправляем кандидату автоматическое поздравление со ссылкой на чат
        await bot.send_message(
            chat_id=user_id,
            text=f"🎉 Поздравляем! Ваша заявка одобрена. Добро пожаловать в команду Pulse.\n"
                 f"Вот ваша постоянная ссылка на чат разработчиков: {DEV_CHAT_LINK}"
        )
        await callback.message.edit_text(callback.message.text + "\n\n✅ **Кандидат принят, ссылка отправлена.**")
    
    elif action == "decline":
        # Отправляем кандидату вежливый отказ
        await bot.send_message(
            chat_id=user_id,
            text="Спасибо за отклик! К сожалению, на данный момент мы не готовы пригласить вас в команду разработки. Желаем удачи!"
        )
        await callback.message.edit_text(callback.message.text + "\n\n❌ **Заявка отклонена.**")
        
    await callback.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
  
