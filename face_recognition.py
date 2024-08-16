# face_recognition.py
import os
from picamera2 import Picamera2
import cv2
import numpy as np
from PIL import Image
import firebase_admin
from firebase_admin import credentials, storage
from datetime import datetime
import io

# 절대 경로 설정
BASE_DIR = '/home/ewha'
HAAR_CASCADE_PATH = os.path.join(BASE_DIR, 'haarcascade/haarcascade_frontalface_default.xml')
TRAINER_PATH = os.path.join(BASE_DIR, 'trainer.yml')

# Firebase 초기화
cred = credentials.Certificate("/home/ewha/locklock-3807d-firebase-adminsdk-1qsjh-2e8d5870f7.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'locklock-3807d.appspot.com'
})

bucket = storage.bucket()

# 얼굴 인식용 Haar Cascade 및 카메라 초기화
faceCascade = cv2.CascadeClassifier(HAAR_CASCADE_PATH)
picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration(main={"size": (640, 480)}))
picam2.start()

# Firebase에 이미지 업로드 함수
def upload_to_firebase(image_data, cloud_file_name):
    _, buffer = cv2.imencode('.jpg', image_data)
    image_io = io.BytesIO(buffer)
    blob = bucket.blob(cloud_file_name)
    blob.upload_from_file(image_io, content_type='image/jpeg')
    print(f"Uploaded to {cloud_file_name} in Firebase.")

# 사용자 등록 함수
def perform_face_registration():
    face_id = "user123"  # 실제로는 이 값을 클라이언트로부터 받아와야 함
    count = 0
    while count < 5:
        frame = picam2.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            if is_face_completely_in_frame((x, y, w, h), frame.shape[1], frame.shape[0]):
                count += 1
                cloud_file_name = f"registered_faces/{face_id}/User.{face_id}.{count}.jpg"
                upload_to_firebase(frame, cloud_file_name)
        if count >= 5:
            break

    # 추가적인 학습 및 등록 작업 수행
    return True
