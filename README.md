# 시스템 상태 알림 및 원격 관리 봇

이 프로젝트는 다양한 시스템 이벤트(SSH 접속, 로그, 환율 변동 등)를 감지하여 텔레그램으로 알림을 보내고, 원격으로 메시지와 파일을 수신하여 관리하는 파이썬 스크립트 모음입니다.

## 주요 기능 및 스크립트

### 1. SSH 로그인/로그아웃 알림 (`ssh_notifier.py`)

- **기능**: SSH를 통한 서버 접속 및 종료 이벤트가 발생할 때 실시간으로 텔레그램 알림을 보냅니다.
- **정보**: 사용자, 접속 IP, 서버 이름, 시간, PID
- **설정**: PAM(Pluggable Authentication Modules)을 통해 SSH 세션 이벤트를 감지합니다.
- **환경변수**: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`

### 2. SSH 로그인 실패 감지 (`auth_monitor.py`)

- **기능**: 시스템 로그(`/var/log/auth.log`)를 실시간으로 감시하여, 비밀번호 오류 등으로 SSH 로그인이 실패할 경우 알림을 보냅니다.
- **정보**: 시도한 사용자 이름, 접속 시도 IP, 서버 이름, 시간
- **설정**: `systemd` 서비스를 통해 백그라운드에서 항상 실행됩니다.
- **환경변수**: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`

### 3. 엔화(JPY) 환율 변동 알림 (`exchange_rate_notifier.py`)

- **기능**: 네이버 금융에서 엔/원 환율 정보를 가져와, 설정된 범위(930원 이하 또는 960원 이상)를 벗어날 경우 알림을 보냅니다.
- **정보**: 기준 시각, 현재 환율
- **설정**: 스케줄러(예: `cron`)를 통해 주기적으로 실행되도록 설정해야 합니다.
- **환경변수**: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`

### 4. 텔레그램 메시지/파일 수신 및 로깅 (`test_recv_message.py`)

- **기능**: 텔레그램 봇으로 전송된 메시지와 파일을 수신하여 서버에 저장하고 기록합니다.
- **동작**:
    - 텍스트 메시지는 `log/YYYY-MM-DD.log` 파일에 시간대별로 기록됩니다.
    - 사진 및 파일은 `log/` 디렉토리에 다운로드됩니다. (파일명 중복 시 자동 넘버링)
    - 허용되지 않은 사용자가 메시지를 보낼 경우, 해당 사용자의 `CHAT_ID`를 `log/new_chat_id.log`에 기록하여 관리자가 확인할 수 있습니다.
- **설정**: `.env` 파일에 `BOT_TOKEN`과 `CHAT_ID`(선택 사항)를 설정합니다. `run_background.sh` 스크립트를 통해 백그라운드 실행이 가능합니다.
- **환경변수**: `.env` 파일 사용 (`BOT_TOKEN`, `CHAT_ID`)

---

## 설정 방법

### 1. 환경변수 설정

각 스크립트는 텔레그램 봇 토큰과 채팅 ID를 환경변수에서 읽어옵니다. 시스템 전역 또는 각 스크립트 실행 환경에 맞게 아래 변수들을 설정해야 합니다.

- `TELEGRAM_BOT_TOKEN`: 텔레그램 `BotFather`로부터 발급받은 봇의 API 토큰
- `TELEGRAM_CHAT_ID`: 알림을 수신할 사용자의 고유 채팅 ID

`test_recv_message.py`의 경우, 프로젝트 루트 디렉토리에 `.env` 파일을 생성하여 관리할 수 있습니다.

```
# .env 파일 예시
BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
CHAT_ID=123456789
```

### 2. 스크립트별 설정

- **`ssh_notifier.py`**: `/etc/pam.d/sshd` 파일에 스크립트를 실행하도록 한 줄을 추가해야 합니다.
- **`auth_monitor.py`**: `systemd` 서비스로 등록하여 부팅 시 자동으로 실행되도록 설정하는 것을 권장합니다.
- **`exchange_rate_notifier.py`**: `cron` 작업을 등록하여 원하는 시간 간격으로 실행되도록 설정합니다.
- **`test_recv_message.py`**: `run_background.sh`를 실행하여 백그라운드 프로세스로 만듭니다. `stop.sh`로 종료할 수 있습니다.

### 3. 필요 라이브러리 설치

```bash
pip install requests beautifulsoup4 python-dotenv python-telegram-bot
```

---

## 사용법

각 스크립트는 독립적으로 실행될 수 있습니다. 필요에 따라 `systemd` 서비스, `cron` 작업, 또는 백그라운드 실행 스크립트(`run_background.sh`)를 사용하여 관리합니다.
