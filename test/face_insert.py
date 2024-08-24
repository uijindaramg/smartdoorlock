import os
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
cred = credentials.Certificate("/home/ewha/locklock-3807d-firebase-adminsdk-1qsjh-2e8d5870f7.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'locklock-3807d.appspot.com'
})

bucket = storage.bucket()

# 얼굴 인식을 위한 Haar Cascade 분류기 불러오기
faceCascade = cv2.CascadeClassifier(HAAR_CASCADE_PATH)

# 사용자 ID와 숫자 ID를 매핑할 딕셔너리
id_to_num = {}
num_to_id = {}
current_id = 0

# 사용자로부터 문자열 ID를 입력받음
face_id = input('\n USER ID 입력하고 엔터 누르세요 ')  # 사용자 ID를 문자열로 입력받음

# 문자열 ID가 이미 매핑되었는지 확인하고, 없으면 새로 매핑
if face_id not in id_to_num:
    id_to_num[face_id] = current_id
    num_to_id[current_id] = face_id
    current_id += 1

# 매핑된 숫자 ID 가져오기
numeric_id = id_to_num[face_id]

# 카메라 초기화 코드 및 얼굴 인식, 학습 로직
picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration(main={"size": (640, 480)}))
picam2.start()

count = 0
print("Starting video stream...")

while count < 5:
    frame = picam2.capture_array()
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        count += 1
        cloud_file_name = f"registered_faces/{numeric_id}/User.{numeric_id}.{count}.jpg"
        _, buffer = cv2.imencode('.jpg', frame)
        image_data = buffer.tobytes()
        blob = bucket.blob(cloud_file_name)
        blob.upload_from_file(io.BytesIO(image_data), content_type='image/jpeg')

    cv2.imshow('image', frame)
    if cv2.waitKey(1) & 0xFF == 27:  # 'ESC' 키를 누르면 종료
        break

cv2.destroyAllWindows()

def getImagesAndLabels():
    blobs = bucket.list_blobs(prefix='registered_faces/')
    faceSamples = []
    ids = []
    for blob in blobs:
        if not blob.name.endswith('.jpg'):
            continue
        image_data = blob.download_as_bytes()
        PIL_img = Image.open(io.BytesIO(image_data)).convert('L')
        img_numpy = np.array(PIL_img, 'uint8')
        numeric_id = int(blob.name.split(".")[1])  # 숫자 ID 추출
        faces = faceCascade.detectMultiScale(img_numpy)
        for (x, y, w, h) in faces:
            faceSamples.append(img_numpy[y:y+h, x:x+w])
            ids.append(numeric_id)
    return faceSamples, ids

faces, ids = getImagesAndLabels()
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.train(faces, np.array(ids))
recognizer.write(TRAINER_PATH)

print("\n [INFO] {0} faces trained. Exiting Program".format(len(np.unique(ids))))
