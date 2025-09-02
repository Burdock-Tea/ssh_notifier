# SSH 접속 알림 봇 설정 가이드

이 문서는 우분투(Ubuntu) 서버에 SSH 연결 시도가 있을 때, 텔레그램(Telegram)으로 알림을 보내는 시스템을 구축하는 방법을 안내합니다.

**기능:**
1.  SSH 로그인 성공 시 알림
2.  SSH 로그아웃 시 알림
3.  SSH 로그인 실패 시 (비밀번호 오류 등) 알림

---

## 1. 사전 준비: 텔레그램 봇 생성

알림을 받기 위해 텔레그램 봇의 **API 토큰**과 사용자의 **채팅 ID**가 필요합니다.

### 1.1. 봇 API 토큰 받기
1.  텔레그램에서 `BotFather`를 검색하여 대화를 시작합니다.
2.  `/newbot` 명령어를 입력하고, 봇의 이름과 사용자 이름을 설정합니다.
3.  생성이 완료되면 BotFather가 알려주는 **HTTP API 토큰**을 복사합니다. (예: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

### 1.2. 채팅 ID 확인하기
1.  방금 만든 봇에게 아무 메시지나 보냅니다.
2.  웹 브라우저에서 아래 URL에 당신의 봇 토큰을 넣어 접속합니다.
    ```
    https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
    ```
3.  JSON 응답에서 `result[0].message.chat.id` 값을 찾아서 복사합니다. (숫자로 된 값입니다)

---

## 2. 서버 설정: 스크립트 및 구성

이제 실제 알림을 보낼 우분투 서버에 접속하여 아래 설정들을 진행합니다.

### 2.1. 공통 설정: 인증 정보 파일 생성

두 종류의 알림 스크립트가 모두 사용할 텔레그램 인증 정보 파일을 생성합니다.

```bash
# /etc/ssh_notifier.conf 파일을 생성하고 아래 내용 입력
sudo nano /etc/ssh_notifier.conf
```

**`/etc/ssh_notifier.conf` 파일 내용:**
```
TELEGRAM_BOT_TOKEN=<1.1에서 발급받은 봇 토큰>
TELEGRAM_CHAT_ID=<1.2에서 확인한 채팅 ID>
```

파일 저장 후, 보안을 위해 소유자와 권한을 변경합니다.
```bash
sudo chown root:root /etc/ssh_notifier.conf
sudo chmod 600 /etc/ssh_notifier.conf
```

### 2.2. 공통 설정: 필요 패키지 설치
```bash
sudo apt update
sudo apt install -y python3 python3-pip
pip3 install requests
```

---

## 3. 로그인 성공/로그아웃 알림 설정 (PAM)

### 3.1. 스크립트 복사 및 권한 설정

`src/ssh_notifier.py` 스크립트는 SSH 로그인 성공 및 로그아웃 이벤트를 감지하여 텔레그램으로 알림을 보냅니다. 서버에 프로젝트 파일을 올린 후, 아래 명령어로 스크립트를 시스템 경로에 복사하고 실행 권한을 부여하세요.

```bash
sudo cp src/ssh_notifier.py /usr/local/bin/ssh_notifier.py
sudo chmod +x /usr/local/bin/ssh_notifier.py
```

### 3.2. PAM 설정

SSH 세션이 시작되거나 끝날 때 스크립트를 실행하도록 PAM 설정을 수정합니다.

```bash
sudo nano /etc/pam.d/sshd
```

`@include common-session` 라인 **아래**에 다음 두 줄을 추가합니다.

```
# SSH Notifier: Load environment variables from config file
session optional pam_env.so envfile=/etc/ssh_notifier.conf
# SSH Notifier: Execute script on login/logout
session optional pam_exec.so seteuid /usr/local/bin/ssh_notifier.py
```

---

## 4. 로그인 실패 알림 설정 (systemd)

### 4.1. 스크립트 복사 및 권한 설정

`src/auth_monitor.py` 스크립트는 시스템 로그를 감시하여 SSH 로그인 실패 이벤트를 감지하고 알림을 보냅니다. 아래 명령어로 스크립트를 시스템 경로에 복사하고 실행 권한을 부여하세요.

```bash
sudo cp src/auth_monitor.py /usr/local/bin/auth_monitor.py
sudo chmod +x /usr/local/bin/auth_monitor.py
```

### 4.2. systemd 서비스 설정

로그 감시 스크립트가 백그라운드에서 항상 실행되도록 `systemd` 서비스를 등록합니다.

```bash
sudo nano /etc/systemd/system/ssh_fail_notifier.service
```

**`/etc/systemd/system/ssh_fail_notifier.service` 파일 내용:**
```ini
[Unit]
Description=SSH Failed Login Notifier
After=network.target

[Service]
ExecStart=/usr/bin/python3 /usr/local/bin/auth_monitor.py
Restart=always
User=root
EnvironmentFile=/etc/ssh_notifier.conf

[Install]
WantedBy=multi-user.target
```

서비스를 활성화하고 시작합니다.
```bash
sudo systemctl daemon-reload
sudo systemctl enable ssh_fail_notifier.service
sudo systemctl start ssh_fail_notifier.service
```

서비스 상태는 아래 명령어로 확인할 수 있습니다.
```bash
systemctl status ssh_fail_notifier.service
```

---

## 5. 최종 테스트

1.  **로그인 실패**: 서버에 일부러 틀린 비밀번호로 접속을 시도합니다. -> "🚨 SSH 로그인 실패 알림" 수신 확인
2.  **로그인 성공**: 올바른 정보로 서버에 SSH 접속합니다. -> "🔒 SSH 로그인 알림" 수신 확인
3.  **로그아웃**: 접속한 세션을 종료합니다. -> "🔓 SSH 로그아웃 알림" 수신 확인

