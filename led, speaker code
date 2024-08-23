#LED, Speaker Code: 경고음 파일 사용 시, 초안
import RPi.GPIO as GPIO
import time
import pygame
from password_config import PASSWORD  # 기존 파일에서 암호를 불러옴

RED_LED_PIN = 17    
GREEN_LED_PIN = 27 
YELLOW_LED_PIN = 22
SPEAKER_PIN = 18  
DOORLOCK_PIN = 21

# GPIO 모드 설정
GPIO.setmode(GPIO.BCM)
GPIO.setup(RED_LED_PIN, GPIO.OUT)
GPIO.setup(GREEN_LED_PIN, GPIO.OUT)
GPIO.setup(YELLOW_LED_PIN, GPIO.OUT)
GPIO.setup(SPEAKER_PIN, GPIO.OUT)
GPIO.setup(DOORLOCK_PIN, GPIO.OUT)

def check_password(input_password):
    return input_password == PASSWORD

def get_keypad_input():
	
    # 여기서 키패드 모듈을 사용하여 입력을 받아야 함
    return input("Enter the password: ")

def passwordin():
    while True:
		    GPIO.output(YELLOW_LED_PIN, GPIO.HIGH)
        GPIO.output(RED_LED_PIN, GPIO.LOW)
        GPIO.output(GREEN_LED_PIN, GPIO.LOW)
		    # 스피커 초기화
				pygame.mixer.init()
				alert_sound = pygame.mixer.Sound("alert.wav")  # 재생할 파일 다운받아놔야함!!
				# 스피커 활성화
		    alert_sound.play()
        input_password = get_keypad_input()  # 키패드 입력 받기
        if check_password(input_password):
            signal = 1  # 비밀번호가 맞으면 신호 1
        else:
            signal = 0  # 비밀번호가 틀리면 신호 0

try:
		passwordin()

def activate_system(signal):
		i=0
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
        i++
    
try:
    while True:
        activate_system(signal)
        time.sleep(1)
        if 0<i and i<5:
		         passwordin()
        elif i>=5:
		        activate_system(0)
		        exit(0)
        
        time.sleep(2)

except KeyboardInterrupt:
    print("사용자에 의한 종료")

finally:
    pygame.mixer.quit()
    GPIO.cleanup()
