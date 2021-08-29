import dht11
import asyncio
from pigpio_dht import DHT11, DHT22

class GpioHandler:
    def __init__(self,parent):
        self.parent = parent 

    async def start_monitoring_weather(self ,interval):
        sensor = DHT11(4)
        while True: 
            data = sensor.read()
            if(data["valid"] == True):
                self.parent.temp = data["temp_f"]
                self.parent.humidity = data["humidity"]
                print(data)
            await asyncio.sleep(interval)
    