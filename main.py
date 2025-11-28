@dp.message()
async def get_id(msg):
    await msg.answer(f"Твой Telegram ID: {msg.from_user.id}")
