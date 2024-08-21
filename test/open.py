import RPi.GPIO as GPIO                    # RPi.GPIO에 정의된 기능을 GPIO명칭으로 사용

GPIO.setmode(GPIO.BCM)                     # GPIO 이름은 BCM 명칭 사용
GPIO.setup(17, GPIO.OUT)                   # GPIO 23 출력으로 설정

GPIO.output(17, True) 
