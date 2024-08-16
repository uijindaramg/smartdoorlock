from flask import Flask, render_template, jsonify, request
from ultrasonic import check_ultrasonic_sensor, cleanup
from face_recognition import perform_face_registration

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/insertuser')
def insert_user():
    return render_template('insertuser.html')

@app.route('/start-registration', methods=['POST'])
def start_registration():
    user_detected = check_ultrasonic_sensor()
    if user_detected:
        return jsonify({"status": "user_detected", "message": "얼굴인식을 시작합니다"})
    else:
        return jsonify({"status": "user_not_detected", "message": "사용자가 감지되지 않았습니다"})

@app.route('/perform-face-recognition', methods=['POST'])
def perform_face_recognition():
    registration_successful = perform_face_registration()
    if registration_successful:
        return jsonify({"status": "success", "message": "정상등록 되었습니다"})
    else:
        return jsonify({"status": "failure", "message": "얼굴 등록에 실패했습니다"})

if __name__ == "__main__":
    try:
        app.run(host='0.0.0.0', port=5000)
    finally:
        cleanup()  # GPIO 리소스 해제
