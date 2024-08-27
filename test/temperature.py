#라이브러리 호출
import Adafruit_DHT as dht
import time

#핀 설정
DHT_PIN=19

while True:
	try:
			humidity,temperature = dht.read_retry(dht.DHT11, DHT_PIN)
			#humidity,temperature = dht.read_retry(dht.DHT22, DHT_PIN)
			time.sleep(10)
			
			print("Temperature: {}C, Humidity: {}%".format(temperature, humidity))
	
	except RuntimeError:
			pass
