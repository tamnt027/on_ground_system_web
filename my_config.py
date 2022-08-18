


class MyConfig:
    
    __instance = None

    @staticmethod
    def get_instance():
        if MyConfig.__instance == None:
            MyConfig.__instance = MyConfig()
        return MyConfig.__instance
    
    
    def __init__(self) -> None:
        if MyConfig.__instance != None:
            raise Exception(f"This is a singleton!")
        else:
            MyConfig.__instance = self 
            
        self.configs = {}
        self.configs['influxdb'] = {}
        self.configs['influxdb']['token'] = '7pr-NRrkdC6pYS7D7N0dyRgWZMW1fHDXKsRS93p8H8fiQawTp14trpL04Gn_95L8bAiAcNusDvR0zMIFFs_Y_Q=='
        self.configs['influxdb']['org'] = "Ant Alliance"
        self.configs['influxdb']['bucket'] = 'chirpstack-data'
        self.configs['influxdb']['url'] = "http://anthouse.ddns.net:8086"
        
    def __getitem__(self, key):
        return self.configs[key]
    
    
