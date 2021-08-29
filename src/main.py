from logging import exception
from gpio_handler import GpioHandler
from console_logging import ConsoleLogger
import websockets
import asyncio
from pigpio_dht import DHT11, DHT22

import json
import dht11
from config import WeatherMonitorConfig

class Main:
    def __init__(self):
        self.times_opened = 0
        self.gpio_handler = GpioHandler(self)
        self.temp = None
        self.humidity = None
        self.logger = ConsoleLogger()
        self.config = WeatherMonitorConfig()
        self.password = None
         
    async def main(self ,restart = False):
        self.logger.start_message("Weather Station")
        if restart != True:
            self.password = input("\nPassword for the server: ")

        websocket = await self.establish_connection()
        connection_response = await self.send_connection_credentials(websocket)

        if connection_response != "success":
            self.logger.log_failed_auth()
        else:
            self.logger.log_passed_auth()
            t1 = loop.create_task(self.test_send_periodic_data_and_listen(websocket))
            t2 = loop.create_task(self.monitor_weather(self.config.weather_check_interval))
            await asyncio.wait([t1,t2])

    async def send_connection_credentials(self,websocket):
        await websocket.send(self.password)
        await websocket.send(self.name_and_type())
        await websocket.send("main")
        connection_response = await websocket.recv()
        return connection_response

    async def monitor_weather(self, interval):
        handler = GpioHandler(self)

        await handler.start_monitoring_weather(interval)

    async def establish_connection(self):
        times_attempted = 1
        while True:
            try:
                return await websockets.connect(f'ws://{self.config.host}:{self.config.port}', ping_interval= None, max_size = 20000000)
            except:
                ConsoleLogger.log_issue_establishing_connection(times_attempted)
                times_attempted += 1
                await asyncio.sleep(6)

    async def test_send_periodic_data_and_listen(self,websocket):
        ran_into_connection_issue = False
        while True:
            try:
                await self.gather_message_and_route(websocket)

            except websockets.WebSocketException as e:
                ConsoleLogger.log_connection_issue()
                ran_into_connection_issue = True
                break
            except Exception as e: 
                print(e)
            await asyncio.sleep(1)
        if ran_into_connection_issue == True:
            await self.main(True)
        quit()

    async def gather_message_and_route(self,websocket):
        message = await asyncio.wait_for(websocket.recv(),5)
        
        if message == "passive_data":
            data_holder = {"temp":self.temp,"humidity":self.humidity}
            self.insert_alert_status(data_holder)
            await websocket.send(json.dumps(data_holder)) 
        elif message == "deactivate":
            await websocket.send("success")
            await self.enter_deactivate_loop(websocket)
            ConsoleLogger.log_deactivation_or_activation("Deactivated by the server!!" , "red")
        elif message == "disconnect":
            await websocket.send("success")
            ConsoleLogger.log_fatal("\nDisconnected by the server!!(by a client)")

    def name_and_type(self):
        data = {"name":self.config.name , "type":"weather_station"}
        return json.dumps(data)

    def insert_alert_status(self,data_holder):
        data_holder["alert_status"] = "alert_not_present"

    async def enter_deactivate_loop(self,websocket):
        while True:
            try:
                message = await asyncio.wait_for(websocket.recv(),5)       
                if message == "activate":
                    await websocket.send("success")
                    ConsoleLogger.log_deactivation_or_activation("Activated by the server!!" , "green")
                    break
            except asyncio.TimeoutError:
                pass
    
if __name__ == "__main__":
    main = Main()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main.main())