#!/bin/bash

# ssh_notifier.py를 백그라운드에서 실행합니다.
# 로그는 nohup.out 파일에 저장됩니다.

cd "$(dirname "$0")"

nohup python3 src/test_recv_message.py &


