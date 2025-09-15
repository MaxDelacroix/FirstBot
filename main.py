import telebot
import requests
import json
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

bot = telebot.TeleBot("botKey")

def get_ai_response(prompt):
    """Получаем ответ от DeepSeek Chat API"""
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": "BER1",
            },
            json={
                "model": "deepseek/deepseek-chat-v3-0324:free",
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=30
        )
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"Ошибка API: {e}")
        return "Извините, не могу обработать запрос. Попробуйте позже."

from gtts import gTTS
import os
import uuid

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        wait_msg = bot.send_message(
            message.chat.id,
            "⏳ Ждите. Готовлю ответ...",
            reply_to_message_id=message.message_id
        )

        # Получаем ответ от ИИ
        ai_response = get_ai_response(message.text)

        # Удаляем сообщение об ожидании
        bot.delete_message(message.chat.id, wait_msg.message_id)

        # Отправляем текст
        bot.reply_to(message, ai_response)

        # Генерируем уникальное имя для файла
        filename = f"voice_{uuid.uuid4()}.mp3"

        # Озвучиваем текст
        tts = gTTS(text=ai_response, lang='ru')
        tts.save(filename)

        # Отправляем mp3 как аудиофайл
        with open(filename, 'rb') as audio:
            bot.send_audio(
                chat_id=message.chat.id,
                audio=audio,
                reply_to_message_id=message.message_id,
                caption="🔊 Озвучка ответа:"
            )

        # Удаляем файл
        os.remove(filename)

    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {str(e)}")

if __name__ == "__main__":
    print("Бот запущен...")
    bot.infinity_polling()
