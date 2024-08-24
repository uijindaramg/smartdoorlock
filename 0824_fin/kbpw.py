import RPi.GPIO as GPIO
import time
import sys
import led_buzzer

inputKeys = 16  #버튼 16개 사용
keyPressed = 0  #키패드 초기화

GPIO.setmode(GPIO.BCM)
SCL_PIN = 6  #SCL 6번 핀에 연결
SD0_PIN = 5  #SD0 5번 핀에 연결

GPIO.setup(SCL_PIN, GPIO.OUT)  #SCL 핀 출력으로 설정
GPIO.setup(SD0_PIN, GPIO.IN)  #SD0 핀 입력으로 설

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
		
	if(keyState>0 and keyState != keyPressed):
		button = keyState
		keyPressed = keyState
		
	else:
		keyPressed = keyState
	
	return (button)
	
try:
	inputPassword = []  # 입력된 비밀번호를 저장할 리스트
	password = [10, 11, 12, 13, 14, 15, 16]  # 정해진 비밀번호
	n = 0  # 입력된 비밀번호의 길이
	attempts = 0
	door = 0  # 문 상태 (0: 닫힘, 1: 열림)
	
	while True:
		key = getKey()
		
		if key > 0:
			if key >=10 and n < 10:
				inputPassword.append(key)
				n += 1
			else:
				print(inputPassword)
				if password == inputPassword:
					print("door open")
					door = 1
					led_buzzer.led_on(3)
					led_buzzer.Buzzer_CEGC()
					time.sleep(1)
					led_buzzer.led_off(3)
				else:
					print("password is not valid")
					door = 0
					attempts += 1
					led_buzzer.led_on(1)
					led_buzzer.Buzzer_BEEP()
					if attempts >= 5:
						print("Password error 5 times. Program exit.")
						sys.exit()
					time.sleep(1)
					led_buzzer.led_off(1)
				inputPassword = []
				n = 0
						
finally:
	GPIO.cleanup()
	inputPassword = []
