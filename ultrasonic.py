# ultrasonic.py
import RPi.GPIO as GPIO
import time

trig = 10
echo = 8

GPIO.setmode(GPIO.BOARD)
GPIO.setup(echo, GPIO.IN)
GPIO.setup(trig, GPIO.OUT)
GPIO.output(trig, GPIO.LOW)

def check_ultrasonic_sensor():
    GPIO.output(trig, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(trig, GPIO.LOW)
    
    stop = 0
    start = 0
    
    while GPIO.input(echo) == GPIO.LOW:
        start = time.time()
    while GPIO.input(echo) == GPIO.HIGH:
        stop = time.time()
    duration = stop -start
    distance = (duration * 340 * 100) / 2
    
    print(f"Measured distance: {distance:.2f} cm")
    
    if 40 < distance < 60:
        return True
    return False

def cleanup():
    GPIO.cleanup()
