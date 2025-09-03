from dotenv import load_dotenv
import requests
import os
import telegram
import asyncio

load_dotenv()

def send_message(token, chat_id, text):
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    payload = {'chat_id': chat_id, 'text': text}
    response = requests.post(url, data=payload)
    return response

BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
MESSAGE = f"Test telegram api"

# send_message(token, chat_id, 'Hello, Telegram!')
bot = telegram.Bot(token=BOT_TOKEN)
#asyncio.run(bot.send_message(chat_id=CHAT_ID, text=MESSAGE))

updates = asyncio.run(bot.getUpdates())

for u in updates:
    print(u.message)