import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardMarkup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = "8519376729:AAF-i59WCmWIVR8ilYafG54Dynow0quokqI"
ADMINS = [836724312,8235933998]

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --------------------
# Хранилище вопросов и состояний
questions = {}  # question_id: {"user_id": int, "text": str, "admin_captured": False, "admin_id": None, "admin_messages": []}
counter = 1
waiting_for_question = {}  # user_id: True, если ждём текст вопроса
waiting_for_answer = {}    # admin_id: qid, если админ отвечает на вопрос

# --------------------
# Reply-клавиатура для пользователей
def main_keyboard():
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="ℹ️ INFO"), KeyboardButton(text="❓ Задать вопрос")]
        ],
        resize_keyboard=True
    )
    return kb

# --------------------
# Команда /start
@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer(
        "🙌 Привет! Я анонимный бот для вопросов от команды Ultimate. Выберите нужную кнопку:",
        reply_markup=main_keyboard()
    )

# --------------------
# Обработка кнопок пользователя
@dp.message()
async def handle_buttons(msg: types.Message):
    user_id = msg.from_user.id
    text = msg.text

    # INFO
    if text == "ℹ️ INFO":
        await msg.answer(
            "ℹ️ Этот бот позволяет задавать вопросы анонимно менеджерам из нашей команды.\n"
            "Менеджеры получают ваш вопрос и когда они ответят, вы получите свой ответ прямо сюда в чат.\n\n"
            "Нажмите ❓ Задать вопрос, чтобы отправить свой вопрос."
        )
        return

    # Задать вопрос
    if text == "❓ Задать вопрос":
        waiting_for_question[user_id] = True
        await msg.answer("🦣 Напиши свой вопрос или жалобу, и он будет отправлен анонимно менеджерам:")
        return

    # Если ждём вопрос от пользователя
    if waiting_for_question.get(user_id):
        global counter
        qid = f"Q{counter}"
        counter += 1

        # Сохраняем вопрос
        questions[qid] = {
            "user_id": user_id,
            "text": msg.text,
            "admin_captured": False,
            "admin_id": None,
            "admin_messages": []  # сообщения админов для редактирования кнопок
        }
        waiting_for_question.pop(user_id)

        # Отправляем всем админам
        for admin in ADMINS:
            kb = InlineKeyboardBuilder()
            kb.button(text="Ответить", callback_data=f"ans_{qid}")
            m = await bot.send_message(
                admin,
                f"❓ Новый вопрос {qid}:\n\n{msg.text}",
                reply_markup=kb.as_markup()
            )
            questions[qid]["admin_messages"].append((admin, m.message_id))

        await msg.answer("✅ Ваш вопрос/жалоба отправлен! Ответ придёт сюда.")
        return

    # Если админ пишет ответ
    if waiting_for_answer.get(user_id):
        qid = waiting_for_answer[user_id]
        user_to = questions[qid]["user_id"]
        await bot.send_message(user_to, f"💬 Ответ на ваш вопрос {qid}:\n\n{msg.text}")
        await msg.answer("✅ Ответ отправлен пользователю!")

        # Удаляем кнопку у всех админов для этого вопроса
        for admin_id, msg_id in questions[qid]["admin_messages"]:
            try:
                await bot.edit_message_reply_markup(chat_id=admin_id, message_id=msg_id, reply_markup=None)
            except:
                pass

        # Чистим состояния
        waiting_for_answer.pop(user_id)
        questions.pop(qid)
        return

# --------------------
# Кнопка "Ответить" для админов
@dp.callback_query(lambda c: c.data.startswith("ans_"))
async def answer_btn(callback: types.CallbackQuery):
    qid = callback.data.split("_")[1]
    admin_id = callback.from_user.id

    # Проверяем, захвачен ли вопрос
    if questions[qid]["admin_captured"]:
        await callback.answer("❌ Этот вопрос уже обрабатывается другим менеджером.", show_alert=True)
        return

    # Захватываем вопрос
    questions[qid]["admin_captured"] = True
    questions[qid]["admin_id"] = admin_id
    waiting_for_answer[admin_id] = qid

    # Убираем кнопку у всех остальных админов
    for other_admin_id, msg_id in questions[qid]["admin_messages"]:
        if other_admin_id != admin_id:
            try:
                await bot.edit_message_reply_markup(chat_id=other_admin_id, message_id=msg_id, reply_markup=None)
            except:
                pass

    await callback.message.answer(f"✏️ Напиши ответ на {qid} в следующем сообщении:")
    await callback.answer()

# --------------------
# Запуск бота
async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
