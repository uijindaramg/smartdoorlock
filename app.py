from flask import Flask, render_template, request, jsonify
import ultrasonic
import face_insert

app = Flask(__name__)
# Firebase, 카메라 및 얼굴 인식 모델 초기화
bucket = face_insert.initialize_firebase()
picam2 = face_insert.initialize_camera()
if picam2 is None:
    raise RuntimeError("Failed to initialize camera")
faceCascade = face_insert.cv2.CascadeClassifier(face_insert.HAAR_CASCADE_PATH)
recognizer = face_insert.cv2.face.LBPHFaceRecognizer_create()


PASSWORD_FILE_PATH = '/home/ewha/password.txt'


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register_user', methods=['GET'])
def register_user():
    return render_template('insertuser.html')

@app.route('/start_ultrasonic', methods=['POST'])
def start_ultrasonic():
    user_present = ultrasonic.check_ultrasonic_sensor()
    
    if user_present:
        return jsonify({"status": "success", "message": "User detected. Starting face recognition..."})
    else:
        return jsonify({"status": "fail", "message": "User not detected. Please stand closer to the sensor."})

@app.route('/start_face_registration', methods=['POST'])
def start_face_registration():
    user_id = request.form.get('userID')
    face_insert.register_face(user_id, picam2, bucket, faceCascade, recognizer)
    # 얼굴 등록 후 모델을 학습시킴
    face_insert.train_faces(bucket, faceCascade, recognizer)
    return jsonify({"status": "success", "message": "Face registered successfully!"})
    
@app.route('/set_password', methods=['GET', 'POST'])
def set_password():
    if request.method == 'POST':
        password = request.form.get('password')
        if len(password) == 8:
            with open(PASSWORD_FILE_PATH, 'w') as f:
                f.write(password)
            return jsonify({"status": "success", "message": "Password saved successfully!"})
        else:
            return jsonify({"status": "fail", "message": "Password must be exactly 8 characters long."})
    return render_template('password.html')
    
@app.route('/get_temp_humidity', methods=['GET'])
def get_temp_humidity():
    data = sensor_data.read_temperature_humidity()  # Call the function from sensor_data module
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
