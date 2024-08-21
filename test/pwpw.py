import RPi.GPIO as GPIO
import time

inputKeys = 16  # 버튼 16개 사용
keyPressed = 0  # 키패드 초기화

GPIO.setmode(GPIO.BCM)
SCL_PIN = 6  # SCL 6번 핀에 연결
SD0_PIN = 5  # SD0 5번 핀에 연결

GPIO.setup(SCL_PIN, GPIO.OUT)  # SCL 핀 출력으로 설정
GPIO.setup(SD0_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # SD0 핀 입력으로 설정, 풀업 저항 사용

def getKey():
    global keyPressed
    button = 0
    keyState = 0
    time.sleep(0.05)
    
    for i in range(inputKeys):
        GPIO.output(SCL_PIN, GPIO.LOW)
        
        if GPIO.input(SD0_PIN) == GPIO.LOW:  # 버튼 눌림 상태 감지
            keyState = i + 1
        
        GPIO.output(SCL_PIN, GPIO.HIGH)
    
    if keyState > 0 and keyState != keyPressed:
        button = keyState
        keyPressed = keyState
    else:
        keyPressed = keyState
    
    return button

try:
    inputPassword = []  # 빈 리스트로 초기화
    while True:
        key = getKey()
        if key > 0:
            if key >= 10:
                # 버튼 번호가 10 이상일 때는 번호를 리스트에 추가
                inputPassword.append(key)
            else:
                # 버튼 번호가 1~9일 때 리스트 출력
                print(f"Current Password List: {inputPassword}")

finally:
    GPIO.cleanup()
