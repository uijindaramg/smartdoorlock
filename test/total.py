import RPi.GPIO as GPIO
import time
from password_config import PASSWORD  # 기존 파일에서 암호를 불러옴

# 핀 번호 설정
RED_LED_PIN = 17    
GREEN_LED_PIN = 27 
YELLOW_LED_PIN = 25
BUZZER_PIN = 4  
DOORLOCK_PIN = 21 

# GPIO 모드 설정
GPIO.setmode(GPIO.BCM)
GPIO.setup(RED_LED_PIN, GPIO.OUT)
GPIO.setup(GREEN_LED_PIN, GPIO.OUT)
GPIO.setup(YELLOW_LED_PIN, GPIO.OUT)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.setup(DOORLOCK_PIN, GPIO.OUT)

# 부저 설정
buzzer = GPIO.PWM(BUZZER_PIN, 1000)  # 1000Hz 주파수로 PWM 생성

# 키패드 설정
inputKeys = 16  # 버튼 16개 사용
keyPressed = 0  # 키패드 초기화
SCL_PIN = 6  
SD0_PIN = 5 

GPIO.setup(SCL_PIN, GPIO.OUT)
GPIO.setup(SD0_PIN, GPIO.IN)

def getKey():
    global keyPressed
    button = 0
    keyState = 0
    time.sleep(0.05)

    for i in range(inputKeys):
        GPIO.output(SCL_PIN, GPIO.LOW)
        
        if not GPIO.input(SD0_PIN):
            keyState = i + 1
        
        GPIO.output(SCL_PIN, GPIO.HIGH)
    
    if keyState > 0 and keyState != keyPressed:
        button = keyState
        keyPressed = keyState
    else:
        keyPressed = keyState
    
    return button

def check_password(input_password):
    return ''.join(map(str, input_password)) == PASSWORD

def passwordin():
    inputPassword = []
    max_length = len(PASSWORD)  # 설정된 비밀번호 길이에 맞춤
    attempt_count = 0
    
    GPIO.output(YELLOW_LED_PIN, GPIO.HIGH)
    GPIO.output(RED_LED_PIN, GPIO.LOW)
    GPIO.output(GREEN_LED_PIN, GPIO.LOW)
    
    # 부저 경고음 재생
    buzzer.start(50)  # 50% 듀티 사이클로 부저 소리 재생
    time.sleep(0.5)   # 0.5초 동안 소리 재생
    buzzer.stop()
    
    while True:
        key = getKey()
        if key > 0:
            if key <= 10 and len(inputPassword) < max_length:  # 비밀번호 입력
                inputPassword.append(key)
                print(f"입력된 숫자: {key}")
            elif key > 10:  # 엔터 키 등의 종료 조건을 가정
                print(f"입력된 비밀번호: {inputPassword}")
                
                if check_password(inputPassword):
                    print("비밀번호가 맞습니다.")
                    return 1  # 비밀번호 일치, 신호 1 반환
                else:
                    print("비밀번호가 틀렸습니다.")
                    inputPassword = []  # 비밀번호 입력 배열 초기화
                    attempt_count += 1
                    if attempt_count >= 5:
                        print("최대 시도 횟수 초과!")
                        return 0  # 신호 0 반환
            else:
                print("비밀번호가 너무 깁니다. 초기화합니다.")
                inputPassword = []  # 비밀번호 입력 배열 초기화

def activate_system(signal):
    if signal == 0:
        GPIO.output(DOORLOCK_PIN, GPIO.LOW) 
        GPIO.output(RED_LED_PIN, GPIO.HIGH) 
        GPIO.output(GREEN_LED_PIN, GPIO.LOW)
        GPIO.output(YELLOW_LED_PIN, GPIO.LOW)
    elif signal == 1:
        GPIO.output(DOORLOCK_PIN, GPIO.HIGH) 
        GPIO.output(RED_LED_PIN, GPIO.LOW) 
        GPIO.output(GREEN_LED_PIN, GPIO.HIGH) 
        GPIO.output(YELLOW_LED_PIN, GPIO.LOW)

try:
    # 시스템 초기화 상태: 도어락 잠금
    GPIO.output(DOORLOCK_PIN, GPIO.LOW)
    
    while True:
        signal = passwordin()  
        activate_system(signal)
        time.sleep(2)

except KeyboardInterrupt:
    print("사용자에 의한 종료")

finally:
    GPIO.cleanup()
