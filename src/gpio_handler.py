import dht11
import asyncio
from pigpio_dht import DHT11, DHT22

class GpioHandler:
    def __init__(self,parent):
        self.parent = parent 

    async def start_monitoring_weather(self ,interval):
        sensor = DHT11(4)
        while True: 

            
            print(sensor.read())
            print("data")
            await asyncio.sleep(10)
    