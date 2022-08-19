from datetime import datetime, tzinfo
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

from my_config import MyConfig


def get_data_query_string(bucket, time_range, measurement,  period,  dev_eui):
    query_string = f"""from(bucket: "{bucket}")
    |> range(start: -{time_range})
    |> filter(fn: (r) => r["_measurement"] == "{measurement}")
    |> filter(fn: (r) => r["_field"] == "value")
    |> filter(fn: (r) => r["application_name"] == "test-application")
    |> filter(fn: (r) => r["dev_eui"] == "{dev_eui}")
    |> filter(fn: (r) => r["f_port"] == "1")
    |> aggregateWindow(every: {period}, fn: last, createEmpty: false)
    |> yield(name: "last")"""
    
    return query_string

class InfluxDbHelper:
    
    __instance = None

    @staticmethod
    def get_instance():
        if InfluxDbHelper.__instance == None:
            InfluxDbHelper.__instance = InfluxDbHelper()
        return InfluxDbHelper.__instance
    
    def __init__(self) -> None:
        self.config = MyConfig.get_instance()
        
        
    def _do_query(self, query):
        time_stamp = []
        values = []
        with InfluxDBClient(url= self.config['influxdb']['url'], token=self.config['influxdb']['token'], org=self.config['influxdb']['org']) as client:
            tables = client.query_api().query(query, org=self.config['influxdb']['org'])
            for table in tables:
                for record in table.records:
                    date = record.get_time()
          
                    time_stamp.append(date.strftime("%Y-%m-%d %H:%M:%S"))
                    values.append(record.get_value())
                    
                    
        return time_stamp, values           
        
        
    def get_sensor_data(self, time_range, measurement,  period,  dev_eui):
        query = get_data_query_string(bucket=self.config['influxdb']['bucket'], 
                                      time_range=time_range, measurement= measurement, period= period, dev_eui= dev_eui)
        
        return self._do_query(query=query)