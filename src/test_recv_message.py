import os
import asyncio
import telegram
import requests
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# 환경 변수에서 봇 토큰 가져오기
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    print("오류: BOT_TOKEN이 설정되지 않았습니다. .env 파일을 확인하세요.")
    exit()

async def main():
    """실시간으로 텔레그램 메시지와 파일을 받아 처리합니다."""
    bot = telegram.Bot(token=BOT_TOKEN)
    print("텔레그램 봇이 메시지 수신을 시작합니다...")

    # 파일을 저장할 디렉토리 생성
    if not os.path.exists('log'):
        os.makedirs('log')
    
    last_update_id = 0
    try:
        updates = await bot.get_updates(timeout=10)
        if updates:
            last_update_id = updates[-1].update_id
    except Exception as e:
        print(f"초기 업데이트 가져오기 실패: {e}")

    while True:
        try:
            updates = await bot.get_updates(offset=last_update_id + 1, timeout=10)
            
            for update in updates:
                if update.message:
                    file_to_download = None
                    original_filename = None

                    # 사진 또는 파일 메시지 확인
                    if update.message.photo:
                        file_to_download = update.message.photo[-1] # 가장 큰 사진
                        original_filename = f"{file_to_download.file_id}.jpg" # 기본 파일명
                    elif update.message.document:
                        file_to_download = update.message.document
                        original_filename = file_to_download.file_name

                    # 파일 다운로드 로직
                    if file_to_download:
                        try:
                            file_info = await bot.get_file(file_to_download.file_id)
                            
                            # API가 제공하는 경로와 원본 파일명에서 확장자 추출
                            _, api_ext = os.path.splitext(file_info.file_path)
                            _, original_ext = os.path.splitext(original_filename)
                            
                            # API 제공 확장자를 우선 사용, 없으면 원본 파일명 확장자 사용
                            ext = api_ext or original_ext or '.dat'
                            
                            # 저장 파일명: file_id + 확장자 (고유성 보장)
                            save_filename = f"{file_to_download.file_id}{ext}"
                            save_path = os.path.join('log', save_filename)

                            response = requests.get(file_info.file_path)
                            if response.status_code == 200:
                                with open(save_path, 'wb') as f:
                                    f.write(response.content)
                                print(f"파일을 수신하여 '{save_path}'에 저장했습니다.")
                            else:
                                print(f"파일 다운로드 실패 (ID: {file_to_download.file_id})")

                        except Exception as e:
                            print(f"파일 처리 중 오류 발생: {e}")
                    
                    # 텍스트 메시지 처리
                    elif update.message.text:
                        print(f"[{update.message.date}] {update.message.from_user.first_name}: {update.message.text}")
                
                # 다음 폴링을 위해 update_id 갱신
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
