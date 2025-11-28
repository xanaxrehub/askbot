from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio

# ======= ВСТАВЬ СВОЙ ТОКЕН =======
TOKEN = "8519376729:AAF-i59WCmWIVR8ilYafG54Dynow0quokqI"
ADMINS = [ ]  # <-- сюда потом вставишь ID админов
# =================================

bot = Bot(token=TOKEN)
dp = Dispatcher()

questions = {}
counter = 1

# ------------------------------
# Старт / приветствие
@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer("Напишите ваш вопрос — он будет отправлен анонимно группе админов.")

# ------------------------------
# Временный хендлер для проверки ID
@dp.message()
async def get_id(msg: types.Message):
    await msg.answer(f"Твой Telegram ID: {msg.from_user.id}")

# ------------------------------
# Обработка вопросов (анонимно)
# Если уберёшь временный хендлер get_id, этот хендлер будет принимать вопросы
# @dp.message()
# async def handle_question(msg: types.Message):
#     global counter
#     question_id = f"Q{counter}"
#     counter += 1
#     questions[question_id] = msg.from_user.id
#     kb = InlineKeyboardBuilder()
#     kb.button(text="Ответить", callback_data=f"ans_{question_id}")
#     for admin in ADMINS:
#         await bot.send_message(
#             admin,
#             f"❓ Новый вопрос {question_id}:\n\n{msg.text}",
#             reply_markup=kb.as_markup()
#         )
#     await msg.answer("Ваш вопрос отправлен! Ответ придёт сюда.")

# ------------------------------
# Обработка кнопки "Ответить"
@dp.callback_query(lambda c: c.data.startswith("ans_"))
async def answer_btn(callback: types.CallbackQuery):
    qid = callback.data.split("_")[1]
    dp["qid"] = qid
    dp["admin"] = callback.from_user.id
    await callback.message.answer(f"✏️ Напиши ответ на {qid} в следующем сообщении:")
    await callback.answer()

# ------------------------------
# Отправка ответа пользователю
@dp.message()
async def send_answer(msg: types.Message):
    if "qid" not in dp:
        return
    if msg.from_user.id != dp["admin"]:
        return
    qid = dp["qid"]
    user_id = questions[qid]
    await bot.send_message(user_id, f"💬 Ответ на ваш вопрос {qid}:\n\n{msg.text}")
    await msg.answer("Ответ отправлен пользователю!")
    del dp["qid"]
    del dp["admin"]

# ------------------------------
# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
