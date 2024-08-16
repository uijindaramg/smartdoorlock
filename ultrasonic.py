# ultrasonic.py
import time

def check_ultrasonic_sensor():
    print("초음파 센서 확인 중...")
    time.sleep(1)  # 센서 확인 시간 시뮬레이션

    # True일 때만 얼굴 등록이 가능하도록
    user_detected = True  # 예를 들어 사용자가 적절한 위치에 있다고 가정
    return user_detected
