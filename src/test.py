import requests
from dotenv import load_dotenv
import os

load_dotenv()

def send_message(token, chat_id, text):
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    payload = {'chat_id': chat_id, 'text': text}
    response = requests.post(url, data=payload)
    return response

token = os.getenv('BOT_TOKEN')
chat_id = os.getenv('CHAT_ID')

send_message(token, chat_id, 'Hello, Telegram!')
