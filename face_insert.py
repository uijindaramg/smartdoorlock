import os
from picamera2 import Picamera2
import cv2
import numpy as np
from PIL import Image
import firebase_admin
from firebase_admin import credentials, storage
import io

# 절대 경로 설정
BASE_DIR = '/home/ewha'
HAAR_CASCADE_PATH = os.path.join(BASE_DIR, 'haarcascade/haarcascade_frontalface_default.xml')
TRAINER_PATH = os.path.join(BASE_DIR, 'trainer.yml')

### Firebase 초기화 함수
def initialize_firebase():
    cred = credentials.Certificate("/home/ewha/locklock-3807d-firebase-adminsdk-1qsjh-2e8d5870f7.json")
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'locklock-3807d.appspot.com'
    })
    return storage.bucket()

### 카메라 초기화 함수
def initialize_camera():
    try:
        picam2 = Picamera2()
        picam2.configure(picam2.create_still_configuration(main={"size": (640, 480)}))
        picam2.start()
        print("Camera initialized successfully.")
        return picam2
    except Exception as e:
        print(f"Failed to initialize camera: {str(e)}")
        return None

# 얼굴이 화면에 완전히 들어오는지 확인하는 함수
def is_face_completely_in_frame(face, frame_width, frame_height):
    x, y, w, h = face
    return x >= 0 and y >= 0 and (x + w) <= frame_width and (y + h) <= frame_height

# 얼굴이 화면의 특정 비율 이상을 차지하는지 확인하는 함수
def is_face_large_enough(face, frame_width, frame_height, min_percentage=0.4):
    x, y, w, h = face
    face_area = w * h
    frame_area = frame_width * frame_height
    face_percentage = face_area / frame_area
    return face_percentage >= min_percentage

### Firebase에 이미지 업로드하는 함수
def upload_to_firebase(image_data, cloud_file_name, bucket):
    _, buffer = cv2.imencode('.jpg', image_data)
    image_io = io.BytesIO(buffer)
    blob = bucket.blob(cloud_file_name)
    blob.upload_from_file(image_io, content_type='image/jpeg')
    print(f"Uploaded to {cloud_file_name} in Firebase.")

### 이미 등록된 사용자 확인하는 함수
def is_user_registered(face_id, bucket):
    user_folder = f"registered_faces/{face_id}/"
    blobs = bucket.list_blobs(prefix=user_folder)
    files = list(blobs)
    if len(files) > 0:
        print(f"User {face_id} is already registered.")
        return True
    else:
        print(f"User {face_id} is not registered.")
        return False

### 얼굴이 이미 등록된 사용자 확인하는 함수
def is_face_already_registered(face_id, recognizer, frame, faceCascade, threshold=60):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
        id, confidence = recognizer.predict(gray[y:y+h, x:x+w])
        if id == int(face_id) and confidence < threshold:
            return True
    return False

### 사용자 얼굴 등록 함수
def register_face(face_id, picam2, bucket, faceCascade, recognizer):
    if is_user_registered(face_id, bucket):
        print("이미 등록된 사용자명입니다.")
        return

    # 첫 번째 이미지 촬영 및 얼굴 중복 확인
    while True:
        frame = picam2.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        if is_face_already_registered(face_id, recognizer, frame, faceCascade):
            print("이미 얼굴 등록이 완료된 사용자입니다.")
            return
        break

    count = 0
    print("Starting video stream...")

    while count < 50:
        try:
            frame = picam2.capture_array()
            if frame is None:
                print("Failed to capture image")
                continue

            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = faceCascade.detectMultiScale(gray, 1.3, 5)
            print(f"Detected faces: {len(faces)}")

            for (x, y, w, h) in faces:
                if is_face_completely_in_frame((x, y, w, h), frame.shape[1], frame.shape[0]) and is_face_large_enough((x, y, w, h), frame.shape[1], frame.shape[0]):
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    count += 1
                    cloud_file_name = f"registered_faces/{face_id}/User.{face_id}.{count}.jpg"
                    upload_to_firebase(frame, cloud_file_name, bucket)

                else:
                    print("Detected face is not completely in the frame or not large enough.")
                
            cv2.imshow('image', frame)

            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # 'ESC' 키를 누르면 종료
                break
        except Exception as e:
            print(f"An error occurred during the video stream: {str(e)}")
            break

    cv2.destroyAllWindows()

### 얼굴 데이터 학습 함수
def getImagesAndLabels(bucket, faceCascade):
    blobs = bucket.list_blobs(prefix='registered_faces/')
    faceSamples = []
    ids = []
    for blob in blobs:
        if not blob.name.endswith('.jpg'):
            continue
        try:
            image_data = blob.download_as_bytes()
            PIL_img = Image.open(io.BytesIO(image_data)).convert('L')
            img_numpy = np.array(PIL_img, 'uint8')
            id = int(blob.name.split(".")[1])
            faces = faceCascade.detectMultiScale(img_numpy)
            for (x, y, w, h) in faces:
                faceSamples.append(img_numpy[y:y+h, x:x+w])
                ids.append(id)
        except Exception as e:
            print(f"Error processing {blob.name}: {str(e)}")
    return faceSamples, ids

def train_faces(bucket, faceCascade, recognizer):
    print("\n [INFO] Training faces. It will take a few seconds. Wait ...")
    faces, ids = getImagesAndLabels(bucket, faceCascade)
    recognizer.train(faces, np.array(ids))
    recognizer.write(TRAINER_PATH)
    print(f"\n [INFO] {len(np.unique(ids))} faces trained. Exiting Program")
