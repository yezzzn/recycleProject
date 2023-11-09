#서버에서 json파일 복사후 아두이노로 명령어 전송

import serial
import time
import os
import subprocess
import json
import time

ssh_key_path = "@@@@@"
remote_server = "ubuntu@@@@@:/home/ubuntu/data.json"
local_file = "data.json"


port = "/dev/ttyUSB1"  # 아두이노 시리얼 포트
serialToArduino = serial.Serial(port, 9600)


print("통신 준비 완료!")
processed_ids = []  

while True:
    # 원격 서버로부터 파일 복사
    command = f'scp -i {ssh_key_path} {remote_server} {local_file}'
    try:
        subprocess.check_call(command, shell=True)
        print("파일을 성공적으로 복사했습니다.")
    except subprocess.CalledProcessError:
        print("파일을 복사하는 동안 오류가 발생했습니다.")

    # "data.json" 파일의 내용을 읽기
    with open("data.json", "r") as json_file:
        data_list = json.load(json_file)

    # 각 명령 처리
    for data in data_list:
        data_id = data["id"]
        data_class = data["class"]
        if data_class == "can":
            current_content = 1
        elif data_class == "glass":
            current_content = 2
        elif data_class == "nocapglass":
            current_content = 3
        elif data_class == "paper":
            current_content = 4
        elif data_class == "plastic":
            current_content = 5
        elif data_class == "plasticlabel":
            current_content = 6

      
        if data_id not in processed_ids:
            # 새 데이터를 아두이노로 보냄
            serialToArduino.write(str(current_content).encode())
            print("data.json에서 메시지를 보냈습니다: " + str(current_content))
            # ID를 배열에 추가하여 중복 전송 방지
            processed_ids.append(data_id)
            print(processed_ids)
    # 일정 시간 대기
    time.sleep(1)  # 1초 간격으로 message.txt를 확인하고 전송합니다.
