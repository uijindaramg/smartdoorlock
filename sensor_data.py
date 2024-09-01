# sensor_data.py
import board
import adafruit_dht

# Initialize the DHT11 device
dht_device = adafruit_dht.DHT11(board.D16)

def read_temperature_humidity():
    try:
        # Read temperature and humidity from DHT11
        temperature_c = dht_device.temperature
        humidity = dht_device.humidity
        
        # Return the readings as a dictionary
        return {"temperature": temperature_c, "humidity": humidity}
    except RuntimeError as error:
        print(f"Error reading DHT11 sensor: {error.args[0]}")
        return {"temperature": None, "humidity": None}
