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
## 수정 : 위치 변경
# 학습 및 얼굴 인식 코드
recognizer = cv2.face.LBPHFaceRecognizer_create()

### firebase에 업로드 하는 코드
def upload_to_firebase(image_data, cloud_file_name):
    _, buffer = cv2.imencode('.jpg', image_data)  # 이미지를 JPG로 인코딩
    image_io = io.BytesIO(buffer)  # 메모리 내에서 이미지 데이터를 다루기 위한 io 객체 생성
    blob = bucket.blob(cloud_file_name)
    blob.upload_from_file(image_io, content_type='image/jpeg')
    print(f"Uploaded to {cloud_file_name} in Firebase.")

## 수정 : 이미 등록된 사용자 이름 여부를 확인하는 함수
def is_user_registered(face_id):
    user_folder = f"registered_faces/{face_id}/"  # 각 사용자의 폴더를 기준으로 확인
    blobs = bucket.list_blobs(prefix=user_folder)
    files = list(blobs)
    if len(files) > 0:
        print(f"User {face_id} is already registered.")
        return True
    else:
        print(f"User {face_id} is not registered.")
        return False

## 수정 : 
# 얼굴이 이미 저장된 사용자인지 확인하는 함수
def is_face_already_registered(face_id, recognizer, frame, threshold=60):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
        id, confidence = recognizer.predict(gray[y:y+h, x:x+w])
        if id == int(face_id) and confidence < threshold:
            return True
    return False


## 수정 : # ID 입력 및 등록 확인 루프
while True:
    face_id = input('\n USER ID 입력하고 엔터 누르세요 ')  # 1부터 입력

    if is_user_registered(face_id):
        print("이미 등록된 사용자명입니다.")
        continue

    ## 수정 :  얼굴이 이미 등록된 경우 메시지 출력하고 다시 입력 단계로 돌아감
    # 첫 번째 이미지 촬영 및 얼굴 중복 확인
    frame = picam2.capture_array()
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    if is_face_already_registered(face_id, recognizer, frame):
        print("이미 얼굴 등록이 완료된 사용자입니다.")
        continue

    break

# 이름 리스트 초기화
## 수정: None만 존재하도록 했는데...None이 필요할까요?
names = ['None']  # 필요한 경우 더 많은 이름을 추가하세요.

count = 0
print("Starting video stream...")

## 수정: 30장-> 50장으로 변경
while count < 5:
    try:
        frame = picam2.capture_array()
        if frame is None:
            print("Failed to capture image")
            continue
        else:
            print("Image captured successfully")

	## 수정: RGB -> BGR 변환 코드 추가 (파란 얼굴 문제 해결)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, 1.3, 5)
        print(f"Detected faces: {len(faces)}")

        for (x, y, w, h) in faces:
            if is_face_completely_in_frame((x, y, w, h), frame.shape[1], frame.shape[0]) and is_face_large_enough((x, y, w, h), frame.shape[1], frame.shape[0]):
		            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
		            count += 1
		            cloud_file_name = f"registered_faces/{face_id}/User.{face_id}.{count}.jpg"
		            upload_to_firebase(frame, cloud_file_name)  # 사용자 폴더에 저장
		            #_, buffer = cv2.imencode('.jpg', gray[y:y+h, x:x+w])
		            #image_data = buffer.tobytes()
		            #upload_to_firebase(image_data, f"registered_faces/User.{face_id}.{count}.jpg")
            else:
                    print("Detected face is not completely in the frame or not large enough.")
                
            
            # 카메라 피드 화면에 표시
            cv2.imshow('image', frame)  # 라즈베리파이 환경에서는 문제가 될 수 있음

        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # 'ESC' 키를 누르거나 30개의 이미지 캡처 후 종료
            break
    except Exception as e:
        print(f"An error occurred during the video stream: {str(e)}")

cv2.destroyAllWindows()

def getImagesAndLabels():
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

print("\n [INFO] Training faces. It will take a few seconds. Wait ...")
faces, ids = getImagesAndLabels()
recognizer.train(faces, np.array(ids))
recognizer.write(TRAINER_PATH)
print("\n [INFO] {0} faces trained. Exiting Program".format(len(np.unique(ids))))
