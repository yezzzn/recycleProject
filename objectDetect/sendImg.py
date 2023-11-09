import cv2
import time
import os
import pymysql

# 사람 확인용 
def checkPerson():
    #db
    conn=pymysql.connect(host="",
                user="",
                passwd="",
                db="")
    cur = conn.cursor()
    # 이제 데이터베이스에서 person 컬럼이 1인지 확인하고 데이터를 가져옵니다
    check_query = "SELECT userName FROM auth_user WHERE person = 1"
    cur.execute(check_query)
    result = cur.fetchone()

# 웹캠을 엽니다 (일반적으로 0은 내장py 웹캠을 가리킵니다)
    if result is not None:
        user = result[0]
        print(user)
        return True
    else:
        print("None")
        return False

def thread_background():
    while True:
        ret, frame = cap.read()
        

while True:
    if checkPerson() == True:
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        ret, frame = cap.read()
        if not ret:
            print("웹캠에서 프레임을 읽을 수 없습니다.")
            break

        # 이미지를 저장할 경로 및 파일 이름
        file_name = "detect.jpg"

        # 이미지를 저장합니다 (프로젝트 디렉토리 내에 저장)
        cv2.imwrite(file_name, frame)

        # scp 명령어를 사용하여 이미지를 EC2 서버로 전송
        os.system(
                f'scp -i "/home/piKHB/.ssh/sshKey.pem"  "{file_name}" ubuntu@43.201.144.233:/home/ubuntu/recycle/project/media/item_images/{file_name}'
        )
        print(f"{file_name} 이미지 저장 및 전송 완료")

        # 2초마다 이미지를 저장하도록 설정
        time.sleep(1)

    else:
        time.sleep(3)
        continue
    time.sleep(2)
    # 작업이 끝나면 웹캠을 해제합니다
    cap.release()
    cv2.destroyAllWindows()

