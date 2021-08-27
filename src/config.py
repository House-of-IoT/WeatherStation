import json
from console_logging import ConsoleLogger
class WeatherMonitorConfig:
    def __init__(self):
        self.host = None
        self.port = None
        self.weather_check_interval = None
        self.name = None
        self.gather_config()

    def gather_config(self):
         with open ("config.json",'r') as File:
             try:
                 data = str(File.read())
                 data_dict = json.loads(data)
                 self.host = data_dict["host"]
                 self.port = data_dict["port"]
                 self.name = data_dict["name"]
                 self.weather_check_interval = data_dict["interval"]
             except Exception as e:
                 print(e)
                 ConsoleLogger.log_fatal("Couldn't locate a config file!")

class ConfigMaker:
    def __init__(self):
        self.logger = ConsoleLogger()
        self.logger.start_message("Weather Station Config Maker")

    def write_config(self,data_dict):
        with open("config.json" , "w") as File:
            data_to_write =json.dumps(data_dict)
            File.write(data_to_write)

    def create_config(self):
        host = input("host:")
        port = input("port:")
        interval = int(input("interval:"))
        name = input("name:")
        data_dict = {"host":host , "port":port , "interval":interval , "name":name}
        self.write_config(data_dict)
        self.logger.log_config_success()

if __name__ == "__main__":
    ConfigMaker().create_config()