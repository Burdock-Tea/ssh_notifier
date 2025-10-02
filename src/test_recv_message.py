import os
import asyncio
import telegram
import requests
from dotenv import load_dotenv
from zoneinfo import ZoneInfo

# .env 파일에서 환경 변수 로드
load_dotenv()

# 환경 변수에서 봇 토큰 및 CHAT_ID 가져오기
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

if not BOT_TOKEN:
    print("오류: BOT_TOKEN이 설정되지 않았습니다. .env 파일을 확인하세요.")
    exit()

async def main():
    """실시간으로 텔레그램 메시지와 파일을 받아 처리합니다."""
    bot = telegram.Bot(token=BOT_TOKEN)
    print("텔레그램 봇이 메시지 수신을 시작합니다...")
    if CHAT_ID:
        print(f"지정된 CHAT_ID({CHAT_ID})의 메시지만 처리합니다.")
    else:
        print("모든 채팅의 메시지를 처리합니다.")

    # 파일을 저장할 디렉토리 생성
    if not os.path.exists('log'):
        os.makedirs('log')
    
    # 마지막으로 처리한 업데이트 ID. 0으로 시작하면 가장 오래된 메시지부터 가져옴.
    last_update_id = 0

    while True:
        try:
            # offset을 사용하여 새로운 업데이트만 가져옴
            updates = await bot.get_updates(offset=last_update_id + 1, timeout=10)
            
            for update in updates:
                if update.message:
                    # CHAT_ID가 설정되어 있거나, 메시지의 chat_id가 일치하는 경우에만 처리
                    if not CHAT_ID or str(update.message.chat.id) == CHAT_ID:
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
                                
                                # 파일명 공백을 언더바로 치환하고, 중복 시 시퀀스 추가
                                save_filename = original_filename.replace(' ', '_')
                                save_path = os.path.join('log', save_filename)

                                # 동일 파일명 존재 시 시퀀스 추가
                                if os.path.exists(save_path):
                                    name, ext = os.path.splitext(save_filename)
                                    i = 1
                                    while True:
                                        new_save_filename = f"{name}_{i:03d}{ext}"
                                        new_save_path = os.path.join('log', new_save_filename)
                                        if not os.path.exists(new_save_path):
                                            save_path = new_save_path
                                            save_filename = new_save_filename
                                            break
                                        i += 1

                                response = requests.get(file_info.file_path)
                                if response.status_code == 200:
                                    with open(save_path, 'wb') as f:
                                        f.write(response.content)
                                    
                                    # 파일 수신 로그 기록 (KST)
                                    kst_time = update.message.date.astimezone(ZoneInfo("Asia/Seoul"))
                                    log_filename = kst_time.strftime('%Y-%m-%d') + ".log"
                                    log_filepath = os.path.join('log', log_filename)
                                    log_entry = f"[{kst_time.strftime('%H:%M:%S')}] 파일 수신: {original_filename} -> {save_path}\n"
                                    
                                    with open(log_filepath, 'a', encoding='utf-8') as f:
                                        f.write(log_entry)

                                    print(f"파일을 수신하여 '{save_path}'에 저장했습니다.")
                                    await bot.send_message(chat_id=update.message.chat.id, text=f"파일 '{original_filename}'이(가) 성공적으로 저장되었습니다.")
                                else:
                                    print(f"파일 다운로드 실패 (ID: {file_to_download.file_id})")
                                    await bot.send_message(chat_id=update.message.chat.id, text=f"파일 '{original_filename}' 다운로드에 실패했습니다.")

                            except Exception as e:
                                print(f"파일 처리 중 오류 발생: {e}")
                                await bot.send_message(chat_id=update.message.chat.id, text=f"파일 '{original_filename}' 처리 중 오류가 발생했습니다.")
                        
                        # 텍스트 메시지 처리
                        elif update.message.text:
                            # 메시지 수신 날짜로 로그 파일 이름 설정 (KST)
                            kst_time = update.message.date.astimezone(ZoneInfo("Asia/Seoul"))
                            log_filename = kst_time.strftime('%Y-%m-%d') + ".log"
                            log_filepath = os.path.join('log', log_filename)
                            
                            # 로그 메시지 형식: [HH:MM:SS] 사용자: 메시지
                            log_entry = f"[{kst_time.strftime('%H:%M:%S')}] {update.message.from_user.first_name}: {update.message.text}\n"
                            
                            # 파일에 로그 추가 (UTF-8 인코딩)
                            with open(log_filepath, 'a', encoding='utf-8') as f:
                                f.write(log_entry)
                                
                            print(f"텍스트 메시지를 '{log_filepath}'에 저장했습니다.")
                    else:
                        # 새로운 CHAT_ID 로깅
                        new_chat_id = update.message.chat.id
                        user_name = update.message.from_user.first_name
                        log_filepath = os.path.join('log', 'new_chat_id.log')
                        
                        # 중복 저장 방지
                        is_already_logged = False
                        try:
                            with open(log_filepath, 'r', encoding='utf-8') as f:
                                for line in f:
                                    if f"New CHAT_ID: {new_chat_id}" in line:
                                        is_already_logged = True
                                        break
                        except FileNotFoundError:
                            pass # 파일이 없으면 그냥 진행

                        if not is_already_logged:
                            log_entry = f"New CHAT_ID: {new_chat_id}, User: {user_name}\n"
                            with open(log_filepath, 'a', encoding='utf-8') as f:
                                f.write(log_entry)
                            print(f"새로운 CHAT_ID({new_chat_id})를 'new_chat_id.log'에 저장했습니다.")
                
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
