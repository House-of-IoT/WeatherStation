import dht11
import asyncio

class GpioHandler:
    def __init__(self,parent):
        self.parent = parent 
        self.instance = dht11.DHT11(pin = 14)

    async def start_monitoring_weather(self ,interval):
        while True: 
            data = self.instance.read()
            c_to_f = (data.temperature * 9/5) + 32
            self.parent.temp = c_to_f
            self.parent.humidity =data.humidity
            await asyncio.sleep(interval)
    