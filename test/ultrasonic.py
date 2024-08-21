import RPi.GPIO as GPIO
import time
import subprocess

# 핀 설정
trig = 23
echo = 24

# GPIO 설정
GPIO.setmode(GPIO.BCM)
GPIO.setup(echo, GPIO.IN)
GPIO.setup(trig, GPIO.OUT)
GPIO.output(trig, GPIO.LOW)

# 초음파 센서 거리 측정
def measure_distance():
    GPIO.output(trig, GPIO.HIGH)
    time.sleep(0.00001)  # 10 마이크로초 신호 발사
    GPIO.output(trig, GPIO.LOW)
    
    start = time.time()
    stop = time.time()
    
    # 에코 핀에서 신호 수신 대기
    while GPIO.input(echo) == GPIO.LOW:
        start = time.time()
    
    while GPIO.input(echo) == GPIO.HIGH:
        stop = time.time()
    
    # 초음파 신호의 왕복 시간을 계산하여 거리 측정
    duration = stop - start
    distance = (duration * 340 * 100) / 2
    
    return distance

# 거리 측정 및 결과 출력
try:
    distance = measure_distance()
    print(f"Measured distance: {distance:.2f} cm")
    
    # 거리 범위 확인 후 face_recognition.py 파일 실행
    if 40 < distance < 60:
        subprocess.run(["python3", "face_recognition.py"])
finally:
    GPIO.cleanup()  # GPIO 설정 정리
