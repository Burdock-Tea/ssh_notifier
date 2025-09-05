#!/bin/bash

# test_recv_message.py 프로세스를 찾아 종료합니다.

PROCESS_NAME="test_recv_message.py"

# 프로세스 ID (PID) 찾기
PID=$(ps aux | grep "[p]ython3 src/$PROCESS_NAME" | awk '{print $2}')

if [ -z "$PID" ]; then
    echo "프로세스가 실행 중이지 않습니다."
else
    echo "프로세스(PID: $PID)를 종료합니다."
    kill $PID
    echo "프로세스가 종료되었습니다."
fi
