import os
import asyncio
import telegram
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# 환경 변수에서 봇 토큰 가져오기
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    print("오류: BOT_TOKEN이 설정되지 않았습니다. .env 파일을 확인하세요.")
    exit()

async def main():
    """실시간으로 텔레그램 메시지를 받아 콘솔에 출력합니다."""
    bot = telegram.Bot(token=BOT_TOKEN)
    print("텔레그램 봇이 메시지 수신을 시작합니다...")
    
    # 마지막으로 처리한 업데이트 ID를 저장하기 위한 변수
    last_update_id = 0

    # getUpdates를 처음 호출하여 가장 최근 update_id를 가져옴
    try:
        updates = await bot.get_updates(timeout=10)
        if updates:
            last_update_id = updates[-1].update_id
    except Exception as e:
        print(f"초기 업데이트 가져오기 실패: {e}")

    while True:
        try:
            # last_update_id + 1을 offset으로 사용하여 새로운 업데이트만 가져옴
            updates = await bot.get_updates(offset=last_update_id + 1, timeout=10)
            
            for update in updates:
                if update.message and update.message.text:
                    print(f"[{update.message.date}] {update.message.from_user.first_name}: {update.message.text}")
                
                # 다음 폴링을 위해 update_id를 갱신
                last_update_id = update.update_id

        except telegram.error.NetworkError as e:
            print(f"네트워크 오류: {e}. 5초 후 재시도합니다.")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"오류 발생: {e}")
            await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("프로그램을 종료합니다.")