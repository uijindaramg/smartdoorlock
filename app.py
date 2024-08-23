from flask import Flask, render_template, request, jsonify
import ultrasonic
import face_insert

app = Flask(__name__)

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
    face_insert.register_face(user_id)
    return jsonify({"status": "success", "message": "Face registered successfully!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
