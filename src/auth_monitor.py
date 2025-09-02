#!/usr/bin/env python3
import os
import time
import re
import requests
import socket
from datetime import datetime

# --- 설정 ---
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
LOG_FILE_PATH = '/var/log/auth.log'
# --- 설정 끝 ---

def send_telegram_message(message):
    """텔레그램 봇으로 메시지를 전송합니다."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return

    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }
    try:
        requests.post(api_url, json=payload, timeout=5)
    except requests.exceptions.RequestException:
        pass

def follow_log(file):
    """tail -f 처럼 파일의 새로운 라인을 계속 읽어옵니다."""
    file.seek(0, os.SEEK_END)
    while True:
        line = file.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line

if __name__ == "__main__":
    # 스크립트 시작 시 간단한 알림을 보내 서비스가 시작되었음을 알립니다.
    hostname = socket.gethostname()
    start_message = f"🛡️ *SSH 실패 감지 서비스 시작* 🛡️\n\n🖥️ *서버*: `{hostname}`"
    send_telegram_message(start_message)

    try:
        with open(LOG_FILE_PATH, 'r') as logfile:
            for line in follow_log(logfile):
                # "Failed password for ... from ..." 패턴을 찾습니다.
                match = re.search(r'Failed password for (invalid user )?(\S+) from (\S+)', line)
                if match:
                    user = match.group(2)
                    ip_address = match.group(3)
                    server_name = socket.gethostname()
                    event_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    message_text = (
                        f"🚨 *SSH 로그인 실패 알림* 🚨\n\n"
                        f"👤 *시도한 사용자*: `{user}`\n"
                        f"🖥️ *서버*: `{server_name}`\n"
                        f"🌐 *접속 시도 IP*: `{ip_address}`\n"
                        f"⏰ *시간*: `{event_time}`"
                    )
                    send_telegram_message(message_text)
    except FileNotFoundError:
        # 로그 파일이 없는 경우, 에러 메시지를 보내고 종료
        error_message = f"❌ *오류*: `{hostname}` 서버에서 로그 파일(`{LOG_FILE_PATH}`)을 찾을 수 없습니다."
        send_telegram_message(error_message)
    except Exception as e:
        # 다른 예외 발생 시 알림
        error_message = f"❌ *오류*: `{hostname}` 서버의 감시 스크립트에서 예외가 발생했습니다.\n`{str(e)}`"
        send_telegram_message(error_message)

