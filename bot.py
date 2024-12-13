import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import ChatMemberUpdatedFilter
from aiogram.types import ChatMemberUpdated, Message, InputFile
from aiogram.dispatcher.router import Router
from random import choice

logging.basicConfig(level=logging.INFO)


API_TOKEN = '7557022926:AAHTZMuLWYPOaI5WnQdfJ9wBgdA2f21tgWM'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()

pending_users = {}

dp.include_router(router)

captcha_images = [
    {"image_path": "captcha1.png", "correct_answer": "WXRGV"},  
    {"image_path": "captcha2.png", "correct_answer": "DkXXP"},  
    {"image_path": "captcha3.png", "correct_answer": "LSYXk"},  
    {"image_path": "captcha4.png", "correct_answer": "N4WW"},  
    {"image_path": "captcha5.png", "correct_answer": "NMXdVV"},  
]

@router.chat_member(ChatMemberUpdatedFilter(member_status_changed=True))
async def on_user_joined(event: ChatMemberUpdated):
    if event.new_chat_member.status == 'member':
        new_user = event.new_chat_member.user
        chat_id = event.chat.id
        user_id = new_user.id

        captcha = choice(captcha_images)
        image_path = captcha["image_path"]
        correct_answer = captcha["correct_answer"]
        
        captcha_message = await bot.send_photo(
            chat_id, 
            InputFile(image_path),
            caption=f"{new_user.full_name}, реши капчу."
        )
        
        pending_users[user_id] = {
            "chat_id": chat_id,
            "captcha_message_id": captcha_message.message_id,
            "correct_answer": correct_answer
        }
        
        try:
            await asyncio.sleep(20)
            if user_id in pending_users:
                await bot.kick_chat_member(chat_id, user_id)
                await bot.send_message(chat_id, f"{new_user.full_name} был заблокирован за неответ на капчу.")
                del pending_users[user_id]
        except Exception as e:
            logging.error(f"Ошибка при ожидании ответа: {e}")

@dp.message()
async def check_captcha(message: Message):
    user_id = message.from_user.id
    if user_id in pending_users:
        correct_answer = pending_users[user_id]["correct_answer"]
        if message.text == str(correct_answer):  
            chat_id = pending_users[user_id]["chat_id"]
            await message.answer("Спасибо за правильный ответ! Добро пожаловать!")
            
            captcha_message_id = pending_users[user_id]["captcha_message_id"]
            await bot.delete_message(chat_id, captcha_message_id)
            
            del pending_users[user_id]
        else:
            await message.answer("Неправильный ответ. Попробуй еще раз.")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
