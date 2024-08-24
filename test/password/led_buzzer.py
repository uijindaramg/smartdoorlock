import RPi.GPIO as GPIO
import time

# 핀 번호 설정
RED_PIN = 17    
GREEN_PIN = 27 
YELLOW_PIN = 25
BUZZER_PIN = 4  

# GPIO 모드 설정
GPIO.setmode(GPIO.BCM)
GPIO.setup(RED_LED_PIN, GPIO.OUT)
GPIO.setup(GREEN_LED_PIN, GPIO.OUT)
GPIO.setup(YELLOW_LED_PIN, GPIO.OUT)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

scale = [523,  554, 587, 622, 659, 698, 740, 784, 831, 880, 932, 988, 1046]

def led_on(color):
  if color == 1:
    GPIO.output(RED_LED, True)
  elif color == 2:
    GPIO.output(YELLOW_LED, True)
  elif color == 3:
    GPIO.output(GREEN_LED, True)

def led_off(color):
  if color == 1:
    GPIO.output(RED_LED, False)
  elif color == 2:
    GPIO.output(YELLOW_LED, False)
  elif color == 3:
    GPIO.output(GREEN_LED, False)

def Buzzer_CEGC():
  buzzer = GPIO.PWM(buzzer_pin, 1)
  buzzer.start(50)
  buzzer.ChangeFrequency(scale[0])
  time.sleep(0.5)
  buzzer.ChangeFrequency(scale[2])
  time.sleep(0.5)
  buzzer.ChangeFrequency(scale[4])
  time.sleep(0.5)
  buzzer.ChangeFrequency(scale[7])
  time.sleep(0.5)
  buzzer.ChangeDutyCycle(0)
  buzzer.stop()
  GPIO.cleanup()

def Buzzer_BEEP():
  buzzer = GPIO.PWM(buzzer_pin, 1000)
  buzzer.start(50)
  time.sleep(1)
  buzzer.stop()
  GPIO.cleanup()

def Buzzer_ROOF():
  buzzer = GPIO.PWM(buzzer_pin, 1000)
  while True:
    buzzer.start(50)
    time.sleep(0.5)
    buzzer.stop()
    time.sleep(0.5)

def Buzzer_OFF():
  buzzer = GPIO.PWM(buzzer_pin, 1)
  buzzer.ChangeDutyCycle(0)
  buzzer.stop()
  GPIO.cleanup()
