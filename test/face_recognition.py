import os
from picamera2 import Picamera2
import cv2
import numpy as np
from PIL import Image
import firebase_admin
from firebase_admin import credentials, storage
from datetime import datetime
import io
import subprocess

# 절대 경로 설정
BASE_DIR = '/home/ewha'
HAAR_CASCADE_PATH = os.path.join(BASE_DIR, 'haarcascade/haarcascade_frontalface_default.xml')
TRAINER_PATH = os.path.join(BASE_DIR, 'trainer.yml')

### Firebase 초기화
cred = credentials.Certificate("/home/ewha/locklock-3807d-firebase-adminsdk-1qsjh-2e8d5870f7.json")  # 다운로드한 서비스 계정 키 파일 경로
firebase_admin.initialize_app(cred, {
    'storageBucket': 'locklock-3807d.appspot.com'  # Firebase 콘솔의 스토리지 버킷 이름. gs://없어도  되는지 확인부탁드요
})

bucket = storage.bucket()

# 라즈베리파이 카메라 초기화
try:
    picam2 = Picamera2()
    picam2.configure(picam2.create_still_configuration(main={"size": (640, 480)}))
    picam2.start()
    print("Camera initialized successfully.")
except Exception as e:
    print(f"Failed to initialize camera: {str(e)}")

# 얼굴 인식을 위한 Haar Cascade 분류기 불러오기
faceCascade = cv2.CascadeClassifier(HAAR_CASCADE_PATH)

# 얼굴이 화면에 완전히 들어오는지 확인하는 함수
def is_face_completely_in_frame(face, frame_width, frame_height):
    x, y, w, h = face
    if x >= 0 and y >= 0 and (x + w) <= frame_width and (y + h) <= frame_height:
        return True
    return False

# 얼굴이 화면의 특정 비율 이상을 차지하는지 확인하는 함수
def is_face_large_enough(face, frame_width, frame_height, min_percentage=0.4):
    x, y, w, h = face
    face_area = w * h
    frame_area = frame_width * frame_height
    face_percentage = face_area / frame_area
    return face_percentage >= min_percentage

### firebase에 업로드 하는 코드
def upload_to_firebase(image_data, cloud_file_name):
    _, buffer = cv2.imencode('.jpg', image_data)  # 이미지를 JPG로 인코딩
    image_io = io.BytesIO(buffer)  # 메모리 내에서 이미지 데이터를 다루기 위한 io 객체 생성
    blob = bucket.blob(cloud_file_name)
    blob.upload_from_file(image_io, content_type='image/jpeg')
    print(f"Uploaded to {cloud_file_name} in Firebase.")

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read(TRAINER_PATH)
picam2.start()  # 카메라 재시작

print("Starting video stream for recognition...")
mismatch_count = 1

while True:
    try:
        frame = picam2.capture_array()
        if frame is None:
            print("Failed to capture image")
            continue
        else:
            print("Image captured successfully")

        ## 수정 : RGB -> BGR 변환 코드 추가 (파란 얼굴 문제 해결)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(int(0.1 * 640), int(0.1 * 480)),
        )
        print(f"Detected faces: {len(faces)}")

				face_found = False
				
        for (x, y, w, h) in faces:
            if is_face_completely_in_frame((x, y, w, h), frame.shape[1], frame.shape[0]) and is_face_large_enough((x, y, w, h), frame.shape[1], frame.shape[0]):
		            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
		            id, confidence = recognizer.predict(gray[y:y+h, x:x+w])
		            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
		
		            if confidence < 40:
		                confidence = f"  {round(100 - confidence)}%"
		                cloud_file_name = f"true_faces/User.{timestamp}_{id}.jpg"
		                upload_to_firebase(frame, cloud_file_name)
		                
		                print("Recognition successful, opening door...")
                    subprocess.run(["python3", "open.py"])
                    face_found = True  # 얼굴이 인식되었음을 표시
                    break
                    
		            else:
		                confidence = f"  {round(100 - confidence)}%"
		                cloud_file_name = f"false_faces/User.{timestamp}.jpg"
		                upload_to_firebase(frame, cloud_file_name) 
		
		            cv2.putText(frame, str(id), (x+5, y-5), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
		            cv2.putText(frame, str(confidence), (x+5, y+h-5), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 1)
        
            else:
                    print("Detected face is not completely in the frame or not large enough.")
        
        if not face_found:
            print(f"Mismatch count: {mismatch_count}")
            mismatch_count += 1
        
        if mismatch_count == 5 :
            print("5 mismatches detected, executing password.py...")
            subprocess.run(["python3", "password.py"])  # password.py 파일 실행
            break
        
        # 얼굴 인식 화면 표시
        cv2.imshow('camera', frame)

        key = cv2.waitKey(100) & 0xFF  # 100으로 증가
        if key == 27:  # 'ESC' 키를 눌러 종료
            break
    except Exception as e:
        print(f"An error occurred during recognition: {str(e)}")

cv2.destroyAllWindows()
