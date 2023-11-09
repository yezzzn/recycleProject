#main 코드

# 객체 검출 후 이미지 파일 크롭하기
# 이미지 파일 각 폴더에 저장하기


# 멀티스레드 + 다중객체 인식 코드
# 다중 객체를 위해 이미지 크롭
import torch
import cv2
import pymysql
import requests
import os
import time
import json
import threading

# DB 연결
conn = pymysql.connect(host="",
                       user="",
                       passwd="",
                       db="")
cur = conn.cursor()

# 첫 번째 모델 초기화
model = torch.hub.load(
    "ultralytics/yolov5",
    "custom",
    "dataAddAllv2.pt",
    force_reload=True,
    skip_validation=True,
)

# 두 번째 모델 초기화
model2 = torch.hub.load(
    "ultralytics/yolov5",
    "custom",
    "label_1025_1434.pt",
    force_reload=True,
    skip_validation=True,
)

# 이미지 파일 저장 경로
model.save_dir = "/home/ubuntu/recycle/project/media/item_images"
model2.save_dir = "/home/ubuntu/recycle/project/media/item_images"

# 이미지 경로 - 현재 빈 화면으로 지정 ------
img = "recycle/project/media/item_images/detect.jpg"

#객체가 없을 때 확인 플래그
noObj = 0

# 이전박스 배열 저장
prev_bboxes = []

# 백그라운드 스레드로 실행할 함수
def detect_objects(img):
    ob_name = None
    results = None
    ob_list = []
    cf_list = []
    data = []
    imgs = []
    filename = []
    i = 1
    
    while True:
        try:
            start_time = time.time()
            # 첫 번째 모델로 객체 검출
            while results is None and time.time() - start_time < 5:  # 최대 5초간 대기
                results = model(img)
                time.sleep(1)  # 1초 대기 후 다시 시도
            # 첫 번째 모델로 객체 검출
            if results is not None:
                detections = []  #  <<----------------------------------클래스명 저장할 리스트
                for idx, detection in enumerate(results.pred[0]):
                    # 바운딩 박스의 좌표 추출
                    x = int(detection[0])  # 바운딩 박스 x1 좌표
                    y1 = int(detection[1])  # 바운딩 박스 y1 좌표
                    x2 = int(detection[2])  # 바운딩 박스 x2 좌표
                    y2 = int(detection[3])  # 바운딩 박스 y2 좌표
                    class_index = int(detection[5])
                    class_name = model.names[class_index]
                    class_conf = float(detection[4])  # 객체 신뢰도 값 가져오기
                    class_conf = round(class_conf, 2)
                    detections.append({"class_name": class_name, "x": x, "x2": x2, "y1" : y1, "y2" : y2, "class_conf": class_conf})
                print("정렬 전-------------")
                print(detections)
                    
                detections.sort(key=lambda x:x["x"]) # <<-------------------- x1기준으로 정렬
                print("정렬 후--------------")
                print(detections)
                # 정렬 후 bbox 데이터 가져오기
                for idx, detection in enumerate(detections):
                    x1 = detection["x"]  # x1 좌표
                    class_name = detection["class_name"]
                    class_conf = detection["class_conf"]
                    print(f"객체 {idx + 1}: {class_name} - x1={x1}, class_conf={class_conf}")
                    
                    # 플라스틱인 경우 모델2로 검출
                    if class_name == 'plastic':
                        for idx, detection in enumerate(detections):
                            # 바운딩 박스의 좌표 추출
                            x11 = int(detection["x"])  # 바운딩 박스 x1 좌표
                            y11 = int(detection["y1"])  # 바운딩 박스 y1 좌표
                            x22 = int(detection["x2"])  # 바운딩 박스 x2 좌표
                            y22 = int(detection["y2"])  # 바운딩 박스 y2 좌표
                         # 이미지 크롭
                        cropped_image = img[y11:y22, x11:x22]
                        
                        # 크롭된 이미지를 모델 2에 전달
                        results2 = model2(cropped_image)
                        pred2 = results2.pandas().xyxy[0]
                        # 플라스틱이 있을 때
                        if results2 is not None:
                            for index, row in pred2.iterrows():
                                print(row['class'], row['confidence'], row['name'])
                                pl_name = row['name']
                                class_conf = row['confidence']
                                class_conf = round(class_conf, 2)
                                if pl_name == 'x':
                                    class_name = 'plastic'
                                else:
                                    class_name = 'plasticlabel'
                                ob_list.append(class_name)
                                print(ob_list)
                                cf_list.append(class_conf)
                                print(cf_list)
                            bboxes = results2.pred[0][:, :4]  
                            for bbox in bboxes:
                                img = results2.render()[0]  # 경계 상자가 있는 이미지 렌더링
                                pt1 = (int(bbox[0]), int(bbox[1]))  # 좌상단 모서리
                                pt2 = (int(bbox[2]), int(bbox[3]))  # 우하단 모서리
                                img = cv2.rectangle(img, pt1, pt2, (0, 255, 0), 2)  # 이미지에 사각형 그리기
                                p_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)     
                                                            # 클래스 이름을 바운딩 박스 위에 출력
                                text_position = (pt1[0], pt1[1] - 10)  # 텍스트 위치 설정
                                cv2.putText(p_img, class_name, text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                                # 이미지 저장 또는 표시
                            output_folder = f"/home/ubuntu/recycle/project/media/item_images/{class_name}"
                            os.makedirs(output_folder, exist_ok=True)  # 해당 클래스명의 폴더가 없으면 생성
                            output_filename = class_name + "n" + ".jpg"
                            def get_next_filename(base_name):
                                # 파일 이름에 "n"을 추가하기 위한 변수 초기화
                                n = 1
                                while True:
                                    # 새로운 파일 이름 생성
                                    new_filename = f"{base_name}{n}.jpg"
                                    # 파일이 이미 존재하는지 확인
                                    if not os.path.exists(output_folder + "/" + new_filename):
                                        return new_filename
                                    n += 1
                            # 기본 파일 이름
                            output_filename = get_next_filename(class_name)
                            filename.append(output_filename)
                            cv2.imwrite(f"{output_folder}/{output_filename}", p_img)
                            print(f"{output_filename} : {class_name} 저장 ")
                            createdBy = "SELECT username FROM auth_user WHERE person=1"
                            cur.execute(createdBy)
                            nameData = cur.fetchone()
                            userName_tuple = nameData[0]  # 첫 번째 행의 튜플
                            userName = str(userName_tuple)  # 문자열로 변환
                    
                            url = (
                                "http://43.201.144.233:8000/example?kind="
                                + class_name  # 종류
                                + "&num="
                                + "1"  # 인식 개수
                                + "&confidence="
                                + str(class_conf)  # 신뢰도
                                + "&created_by="
                                + str(userName)  # 사용자 이름
                                + "&image="
                                + "item_images/" 
                                + f"{class_name}/{output_filename}"  # 이미지 경로
                            )
                            url = str(url)
                            response = requests.get(url)
                            
                                
                    else:
                        ob_list.append(class_name)
                        print(ob_list)
                        cf_list.append(class_conf)
                        print(cf_list)
                        bboxes = results.pred[0][:, :4]
                        # 경계 상자 그리기
                        for bbox in bboxes:
                            img = results.render()[0]  # 경계 상자가 있는 이미지 렌더링
                            pt1 = (int(bbox[0]), int(bbox[1]))  # 좌상단 모서리
                            pt2 = (int(bbox[2]), int(bbox[3]))  # 우하단 모티지
                            img = cv2.rectangle(img, pt1, pt2, (0, 255, 0), 2)  # 이미지에 사각형 그리기
                            f_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)     
                        # 이미지 크롭
                        x1 = int(detection["x"])  # 바운딩 박스 x1 좌표
                        y1 = int(detection["y1"])  # 바운딩 박스 y1 좌표
                        x2 = int(detection["x2"])  # 바운딩 박스 x2 좌표
                        y2 = int(detection["y2"])  # 바운딩 박스 y2 좌표
                        cropped_image = img[y1:y2, x1:x2]
                        f_img = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB) 
                        output_folder = f"/home/ubuntu/recycle/project/media/item_images/{class_name}"
                        os.makedirs(output_folder, exist_ok=True)  # 해당 클래스명의 폴더가 없으면 생성
                        output_filename = class_name + "n" + ".jpg"
                        filename.append(output_filename)
                        def get_next_filename(base_name):
                            # 파일 이름에 "n"을 추가하기 위한 변수 초기화
                            n = 1
                            while True:
                                # 새로운 파일 이름 생성
                                new_filename = f"{base_name}{n}.jpg"
                                # 파일이 이미 존재하는지 확인
                                if not os.path.exists(output_folder + "/" + new_filename):
                                    return new_filename
                                n += 1
                        # 기본 파일 이름
                        output_filename = get_next_filename(class_name)
                        # 이미지 저장
                        cv2.imwrite(f"{output_folder}/{output_filename}", f_img)
                        print(f"{output_filename} : {class_name} 저장 ")
                        
                        createdBy = "SELECT username FROM auth_user WHERE person=1"
                        cur.execute(createdBy)
                        nameData = cur.fetchone()
                        userName_tuple = nameData[0]  # 첫 번째 행의 튜플
                        userName = str(userName_tuple)  # 문자열로 변환
                
                        url = (
                            "http://43.201.144.233:8000/example?kind="
                            + class_name  # 종류
                            + "&num="
                            + "1"  # 인식 개수
                            + "&confidence="
                            + str(class_conf)  # 신뢰도
                            + "&created_by="
                            + str(userName)  # 사용자 이름
                            + "&image="
                            + "item_images/" 
                            + f"{class_name}/{output_filename}"  # 이미지 경로
                        )
                        url = str(url)
                        response = requests.get(url)
                        
                # db에 저장된 id 마지막 값 가져오기
                idSel = "SELECT id FROM item_database ORDER BY id DESC LIMIT 1"
                cur.execute(idSel)
                idData = cur.fetchone() 
                idName = idData[0]  # 첫 번째 행의 튜플
                
                for ob_name, ob_conf in zip(ob_list, cf_list):
                    new_data = {"class": ob_name, "conf": ob_conf, "id": idName + i}
                    data.append(new_data)
                    i = i + 1
                
                if len(data) == 3:
                    with open('data.json', 'w') as json_file:
                        json.dump(data, json_file, indent=2)
                    print("json 파일 저장 완료")
                    print("ob list 초기화")
                    data = []
                    ob_list = []
                    cf_list = []
                    detections = []
                time.sleep(5)
            # 객체가 5초간 인식 안 되는 경우
            else:
                noObj = noObj + 1
                if noObj >= 5:
                    query = "UPDATE auth_user SET person = 0"
                    cur.execute(query)
                    conn.commit()
                    noObj = 0
                time.sleep(5)
                continue        
            
            bboxes_sorted = sorted(bboxes, key=lambda x: x[0])

            # 정렬된 결과 출력
            for bbox in bboxes_sorted:
                print(bbox)

            for idx, bbox in enumerate(bboxes_sorted):
                if pt1[0] == bbox[0]:  # pt1의 x 좌표와 bbox의 첫 번째 데이터 비교
                    print("pt1 x 좌표, bbox의 첫 번째 데이터 비교해서 같은 경우")
                
                if ob_list is not None:
                    for ob_name in ob_list:
                        output_folder = "/home/ubuntu/recycle/project/media/item_images"
                        output_filename = ob_name + "n" + ".jpg"

                        def get_next_filename(base_name):
                            # 파일 이름에 "n"을 추가하기 위한 변수 초기화
                            n = 1
                            while True:
                                # 새로운 파일 이름 생성
                                new_filename = f"{base_name}{n}.jpg"
                                # 파일이 이미 존재하는지 확인
                                if not os.path.exists(output_folder + "/" + new_filename):
                                    return new_filename
                                n += 1
                        # 기본 파일 이름
                        output_filename = get_next_filename(ob_name)
                        if ob_name == 'plastic' or ob_name == 'plasticlabel':
                            # 결과 저장
                            cv2.imwrite(
                                "/home/ubuntu/recycle/project/media/item_images/" + output_filename, p_img
                            )
                        else:
                            # 결과 저장
                            cv2.imwrite(
                                "/home/ubuntu/recycle/project/media/item_images/" + output_filename, f_img
                            )
                    createdBy = "SELECT username FROM auth_user WHERE person=1"
                    cur.execute(createdBy)
                    nameData = cur.fetchone()
                    userName_tuple = nameData[0]  # 첫 번째 행의 튜플
                    userName = str(userName_tuple)  # 문자열로 변환
                    
                    for ob_name, ob_conf in zip(ob_list, cf_list):
                        ob_conf = round(ob_conf, 2)
                        url = (
                            "http://43.201.144.233:8000/example?kind="
                            + ob_name  # 종류
                            + "&num="
                            + "1"  # 인식 개수
                            + "&confidence="
                            + str(ob_conf)  # 신뢰도
                            + "&created_by="
                            + str(userName)  # 사용자 이름
                            + "&image="
                            + "item_images/" + output_filename  # 이미지 경로
                        )
                        url = str(url)
                        response = requests.get(url)
                    time.sleep(15)
                    
        except FileNotFoundError:
            print("FileNotFoundError: 'detect.jpg'")

# 백그라운드 스레드 시작
background_thread = threading.Thread(target=detect_objects,  args=(img,))
background_thread.start()

# 메인 스레드는 다른 작업을 수행
while True:
    user_input = input("Enter a command: ")
    if user_input == "quit":
        # 백그라운드 스레드를 종료하고 프로그램 종료
        background_thread.join()
        break
