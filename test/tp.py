import Adafruit_DHT as dht

# 핀 설정
DHT_PIN = 19

# 센서 타입 설정 (DHT11 또는 DHT22)
SENSOR_TYPE = dht.DHT11

humidity, temperature = dht.read_retry(SENSOR_TYPE, DHT_PIN)

if humidity is not None and temperature is not None:
    print("Temperature: {}C, Humidity: {}%".format(temperature, humidity))
else:
    print("Failed to retrieve data from the sensor")
