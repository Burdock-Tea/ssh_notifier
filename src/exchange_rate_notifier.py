#!/usr/bin/env python3
import os
import requests
import datetime
from bs4 import BeautifulSoup

# --- 설정 ---
# 환경 변수에서 텔레그램 봇 토큰과 채팅 ID를 가져옵니다.
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
# --- 설정 끝 ---

def send_telegram_message(message):
    """텔레그램 봇으로 메시지를 전송합니다."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("오류: 텔레그램 봇 토큰 또는 채팅 ID가 환경 변수에 설정되지 않았습니다.")
        return

    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }
    try:
        response = requests.post(api_url, json=payload, timeout=10)
        # HTTP 에러 발생 시 예외를 발생시킵니다.
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"오류: 텔레그램 메시지 전송에 실패했습니다. - {e}")

def get_jpy_krw_from_naver():
    """
    네이버 금융에서 JPY/KRW 환율 정보를 스크레이핑하여 가져옵니다.
    (100엔당 원화 기준)
    """
    try:
        url = "https://finance.naver.com/marketindex/exchangeDetail.naver?marketindexCd=FX_JPYKRW"
        # 헤더를 추가하여 봇으로 인식되는 것을 방지합니다.
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        # 환율 정보가 있는 p 태그와 em 태그를 선택합니다.
        rate_element = soup.select_one("p.no_today em")

        if rate_element:
            # 쉼표(,)를 제거하고 숫자로 변환합니다.
            rate_str = rate_element.get_text().replace(',', '')
            return float(rate_str)
        
        print("오류: 환율 정보 엘리먼트를 찾지 못했습니다.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"오류: 네이버 금융 페이지를 가져오는 데 실패했습니다. - {e}")
        return None
    except Exception as e:
        print(f"오류: 환율 정보를 파싱하는 데 실패했습니다. - {e}")
        return None

if __name__ == "__main__":
    # 날짜와 시간을 "YYYY년 MM월 DD일 HH:MM:SS" 형식으로 가져옵니다.
    now_str = datetime.datetime.now().strftime("%Y년 %m월 %d일 %H:%M:%S")
    
    # 네이버에서 환율 정보를 가져옵니다.
    rate = get_jpy_krw_from_naver()

    # 환율 정보를 성공적으로 가져왔고, 지정된 임계값을 벗어났는지 확인합니다.
    if rate is not None and (rate <= 920 or rate >= 960):
        # 조건을 만족할 때만 메시지를 생성하고 전송합니다.
        message = (
            f"💴 *JPY/KRW 환율 변동 알림* 💴\n\n"
            f"🗓️ *기준 시각*: {now_str}\n"
            f"📈 *현재 환율*: 100엔 = `{rate:.2f}`원\n\n"
            f"⚠️ 설정된 범위(920원 이하 또는 960원 이상)를 벗어났습니다."
        )
        send_telegram_message(message)
    # else: 환율이 범위 내에 있거나 조회에 실패한 경우, 아무 작업도 하지 않고 종료합니다.
