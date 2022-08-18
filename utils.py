import datetime
from typing import List
from models import MasterValve, Pump, User, Sensor, Chart
from init import db
import hashlib

from my_enum import MasterValveType, PumpType

def get_user_by_id(user_id):
    return User.query.get(user_id)


def check_login(username, password):
    if username and password:
        password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
        
        return User.query.filter(User.username.__eq__(username.strip()),
                                 User.password.__eq__(password),
                                 User.active.__eq__(True)).first()
        
        
def get_master_valve(valve_type : MasterValveType) ->MasterValve: 
    return MasterValve.query.filter(MasterValve.valve_type.__eq__(valve_type)).first()
    
    
def get_pump(pump_type : PumpType) -> Pump:
    return Pump.query.filter(Pump.pump_type.__eq__(pump_type)).first()
    
    
def get_sensors(sensor_id : int) -> Sensor:
    return Sensor.query.get(sensor_id)

def get_chart(chart_id : int) -> Chart:
    return Chart.query.get(chart_id)

def get_active_charts() -> List[Chart]:
    return Chart.query.filter_by(active=True).all()


def convert_timestamp_to_date_string(timestamp):
    date = datetime.datetime.fromtimestamp(timestamp)
    return date.strftime("%d/%m %H:%M")