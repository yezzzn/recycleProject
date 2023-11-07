import threading
import RPi.GPIO as GPIO
import cv2
import numpy as np
import sys
import face_recognition
import pandas as pd
import time
import os
import pymysql
import board
import busio
import digitalio
import adafruit_ssd1306 

from PIL import Image,ImageDraw,ImageFont
from datetime import datetime

unknown_count = 0
frame_count = 0 
text = "abcde"

# 백그라운드에서 돌아가는 led 3초간 지속 함수 
def led_OnOff_3sec():
    GPIO.output(led_red,1)
    time.sleep(3)
    GPIO.output(led_red,0)

# OLED 함수 
def show_oled():
    global text
    print("함수 호출")
    # OLED 디스플레이 설정
    font = ImageFont.truetype('/home/pi/webapps/OLED_Stats/PixelOperator.ttf', 30) 
    
    oled_reset = digitalio.DigitalInOut(board.D4)
    i2c = busio.I2C(board.SCL, board.SDA)
    oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, reset=oled_reset)
    
    oled.fill(0)
    oled.show() 
    
    image = Image.new('1', (oled.width, oled.height))
    draw = ImageDraw.Draw(image)
    
    draw.text((0,0) , text, font=font ,fill = 255)
    oled.image(image)
    oled.show()
    
    time.sleep(4)  #class 에 있는 사람이 인식되면 OPEN 을 3초간 표시 후 초기화
                   #class 에 없는사람이 인식되면 Unknown 을 3초간 표시 후 초기화
    oled.fill(0)
    oled.show()

# 카메라 off 
def End_system():
    if cap is not None:    
        cap.release()
    cv2.destroyAllWindows()
    conn.commit()
    conn.close()
    GPIO.cleanup()


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


sensor = 14
led_red = 21
GPIO.setup(sensor,GPIO.IN)
GPIO.setup(led_red,GPIO.OUT)

# OLED 디스플레이 설정
oled_reset = digitalio.DigitalInOut(board.D4)
i2c = busio.I2C(board.SCL, board.SDA)
oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, reset=oled_reset)
oled.fill(0)
oled.show()

# 폰트 설정
font = ImageFont.truetype('/home/pi/webapps/OLED_Stats/PixelOperator.ttf', 12) 

# 현재 날짜와 시간 가져오기
current_datetime = datetime.now()

#EC2 서버의 DB로 접근
#host=서버주소, user=사용자, passwd=서버암호, db=데이터베이스, 스키마 이름, charset=문자세트(utf8)
conn=pymysql.connect(host="",
                    user="",
                    passwd="",
                    db="")

#DB 접근 시 사용 지정
cur = conn.cursor()


# 검색 할 샘플 사진을 로드 후 인코딩

onestar_image = face_recognition.load_image_file("asset/images/onestar.jpg")
onestar_face_encoding = face_recognition.face_encodings(onestar_image)[0]

bum_image = face_recognition.load_image_file("asset/images/bum.jpg")
bum_face_encoding = face_recognition.face_encodings(bum_image)[0]

hun_image = face_recognition.load_image_file("asset/images/hun.jpg")
hun_face_encoding = face_recognition.face_encodings(hun_image)[0]

minwoo_image = face_recognition.load_image_file("asset/images/minwoo.jpg")
minwoo_face_encoding = face_recognition.face_encodings(minwoo_image)[0]




# 검색 할 얼굴 인코딩 및 이름 배열 생성
known_face_encodings = [
    onestar_face_encoding,
    bum_face_encoding,
    hun_face_encoding,
    minwoo_face_encoding,
]
known_face_names = [
    "onestar",
    "bum",
    "hun",
    "minwoo",
]

# flag를 false 로 초기화
flag = False

# 적외선 센서 인식했을 때
def Status_of_the_sensor():
    global flag,cap
    if GPIO.input(sensor) == 1:
        print("sensor High")
        flag = True
        
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
    #센서인식 X 경우
    elif GPIO.input(sensor) == 0:
        print("sensor Low")
        flag = False 
        cap = None
        print("sensor low")

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap = None              # cap 초기화
    
GPIO.output(led_red,0) # led off로 초기화
try:
    while True:
        Status_of_the_sensor()      
        print(flag)
        while cap is not None and cap.isOpened():
            success, frame = cap.read()
            frame = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
            frame.flags.writeable = False

            # 프레임 미인식 시
            if not success:
                print("웹캠에서 프레임을 읽을 수 없습니다.")
                break


            face_locations = face_recognition.face_locations(frame)
            face_encodings = face_recognition.face_encodings(frame, face_locations)

            frame.flags.writeable = True
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            # bbox 처리 코드
            for (top, right, bottom, left), face_encoding in zip(
                face_locations, face_encodings
            ):
                color = (0, 255, 0)
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)

                name = "Unknown"
                

                face_distances = face_recognition.face_distance(
                    known_face_encodings, face_encoding
                )
                best_match_index = np.argmin(face_distances)

                if matches[best_match_index]:
                    name = known_face_names[best_match_index]

                # 얼굴에 Bounding Box 그리기
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

                # 얼굴 하단에 이름 레이블 그리기
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (0, 0, 0), 1)

                # 인식된 얼굴의 이름이 class에 존재할 경우_
                if name != "Unknown":
                    color = (0, 255, 0)
                    print("인식 됨")
                    # 이미지를 저장할 경로 및 파일 이름
                    file_name = (f"{name}.jpg")
                    # 이미지를 저장합니다 (프로젝트 디렉토리 내에 저장)
                    cv2.imwrite(file_name, frame)

                    # scp 명령어를 사용하여 이미지를 EC2 서버로 전송.
                    os.system(
                    f'scp -i "/home/pi/.ssh/sshKey.pem"  "{file_name}" {file_location}/{file_name}'
                    )
                    print(f"{file_name} 이미지 저장 및 전송 완료")
                    sql = "UPDATE auth_user SET person = 1 WHERE username = %s"
                    conn.commit()
                    data = (name)
                    cur.execute(sql, data)

                    text = "OPEN"
                #class에 있는 얼굴이 아닌 경우
                else:
                    color = (0, 0, 255)
                    print("Unknown ")
                    text = "Unknown"
                    cv2.imwrite("Unknown.jpg", frame)
                    t = threading.Thread(target = led_OnOff_3sec)
                    t.start()    # led on/off 뒤로돌림
                show_oled()




            if flag is False:
                break
        while cap is None:
            Status_of_the_sensor()
            if flag is True:
                break

            
        frame_count += 1
        
        # 매 1초마다 이미지를 저장
        if frame_count % 30 == 0:  # 1초에 30프레임
            cv2.imwrite("face.jpg", frame)

            
        if cv2.waitKey(5) & 0xFF == 27:
            break
        # 1초마다 이미지를 저장하도록 설정
        time.sleep(1)
# except KeyboardInterrupt:
#     if cap is not None:    
#         cap.release()
#     cv2.destroyAllWindows()
#     conn.close()
#     GPIO.cleanup()
except Exception as e:
    print(f"에러 발생: {e}")
    





