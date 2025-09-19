#!/usr/bin/env python3
import os
import requests
import datetime
import socket

# --- 설정 ---
# 아래 두 변수는 직접 설정하는 대신, 보안을 위해 환경 변수에서 가져옵니다.
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
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

def get_session_info():
    """SSH 세션 정보를 수집합니다."""
    try:
        user = os.environ.get('PAM_USER', 'N/A')
        remote_host = os.environ.get('PAM_RHOST', 'N/A')
        
        if not remote_host or remote_host == 'N/A':
            ssh_connection = os.environ.get('SSH_CONNECTION')
            if ssh_connection:
                remote_host = ssh_connection.split(' ')[0]

        hostname = socket.gethostname()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return user, remote_host, hostname, timestamp
    except Exception:
        return 'N/A', 'N/A', 'N/A', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if __name__ == "__main__":
    pam_type = os.environ.get('PAM_TYPE')
    user, client_ip, server_name, event_time = get_session_info()
    
    message_text = ""

    if pam_type == "open_session":
        message_text = (
            f"🔒 *SSH 로그인 알림* 🔒\n\n"
            f"👤 *사용자*: `{user}`\n"
            f"🖥️ *서버*: `{server_name}`\n"
            f"🌐 *접속 IP*: `{client_ip}`\n"
            f"⏰ *시간*: `{event_time}`\n"
            f"⚙️ *PID*: `{os.getppid()}`"
        )
    elif pam_type == "close_session":
        message_text = (
            f"🔓 *SSH 로그아웃 알림* 🔓\n\n"
            f"👤 *사용자*: `{user}`\n"
            f"🖥️ *서버*: `{server_name}`\n"
            f"🌐 *접속 IP*: `{client_ip}`\n"
            f"⏰ *시간*: `{event_time}`\n"
            f"⚙️ *PID*: `{os.getppid()}`"
        )

    if message_text:
        send_telegram_message(message_text)

