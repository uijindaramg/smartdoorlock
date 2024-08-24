import RPi.GPIO as GPIO                    # RPi.GPIO에 정의된 기능을 GPIO명칭으로 사용
import time
import sys

GPIO.setmode(GPIO.BCM)                     # GPIO 이름은 BCM 명칭 사용
GPIO.setup(21, GPIO.OUT)                   # GPIO 23 출력으로 설정

DL_PIN = 21
OPEN = 1
CLOSE = 0

def doorControl(signal):
	if signal == OPEN:
		GPIO.output(DL_PIN, True)  # 핀에 전압 공급 (문 열림)
	elif signal == CLOSE:
		GPIO.output(DL_PIN, False)  # 핀에서 전압 차단 (문 닫힘)

try:
	doorControl(OPEN)
	time.sleep(3)
	doorControl(CLOSE)
	time.sleep(3)
	
finally:
	GPIO.cleanup()

sys.exit()
