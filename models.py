from email.policy import default
import random
import time
from tokenize import group
from unicodedata import name
from sqlalchemy import Column
from init import db
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Enum, UniqueConstraint
from sqlalchemy.orm import relationship, backref
from datetime import datetime
from my_enum import ADSAddress, ADSPin, ChartMode, ChartType, ChartYAxis, IOType, MasterValveType, PCF8575Address, PCF8575Pin, PumpType, TaskStatus, TaskType, UserRole
from my_enum import MyColor
from flask_login import UserMixin
import hashlib
from sqlalchemy import event
from my_exception import NotImplementYetException

from pcf8575_manager import PCF8575Manager



class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    username =  Column(String(50), nullable=False, unique=True)
    password =  Column(String(50), nullable=False)
    active = Column(Boolean, default=True)
    joined_date =  Column(DateTime, default=datetime.now())
    avatar_img = Column(String(128))
    user_role = Column(Enum(UserRole), default=UserRole.USER)
        
    def __repr__(self) -> str:
        return f"User {self.name}"
    
@event.listens_for(User.password, 'set', retval=True)
def hash_user_password(target, value, oldvalue, initiator):
    if value != oldvalue:
        return str(hashlib.md5(value.strip().encode('utf-8')).hexdigest())
    return value


class Group(db.Model):
    __tablename__ = 'groups'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False) 
    description = Column(String(255))
    active = Column(Boolean, default=True)
    image = Column(String(128))
    created_date = Column(DateTime, default=datetime.now())
    has_valves = db.relationship('Valve', secondary='groups_valves', lazy = True, backref = backref('belong_groups', lazy = True))
        
    def __repr__(self) -> str:
        return f"Group {self.name}"
    
    def open_valves(self):
        for valve in self.has_valves:
            if valve.is_open() == False:
                valve.open()
    
    def close_valves(self):
        for valve in self.has_valves:
            if valve.is_open() == True:
                valve.close()

class Valve(db.Model):
    __tablename__ = 'valves'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String(255))
    name = Column(String(50), nullable=False)
    active = Column(Boolean, default=True)
    io_type = Column(Enum(IOType), nullable=False, default = IOType.PCF8575)
    image = Column(String(128))
    
    created_date = Column(DateTime, default=datetime.now())
    
    ads_id = Column(Integer, ForeignKey("ads.id"))
    pcf_id = Column(Integer, ForeignKey("pcf8575.id"))
    mqtt_id = Column(Integer, ForeignKey("mqtt.id"))
    lora_id = Column(Integer, ForeignKey("lora.id"))
    
    ads = db.relationship("ADS", backref="valve", uselist=False, lazy=True)
    pcf8575 = db.relationship("PCF8575", backref="valve", uselist=False,lazy=True)
    mqtt = db.relationship("Mqtt", backref="valve", uselist=False, lazy=True)
    lora = db.relationship("Lora", backref="valve", uselist=False, lazy=True)

        
    def __init__(self,**kwargs):
        super(Valve, self).__init__(**kwargs)
    
    def __repr__(self) -> str:
        return f"Valve {self.name}"
    
    def is_open(self) -> bool:
        if self.io_type == IOType.PCF8575:
            return self.get_pin_state()
    
        elif self.io_type == IOType.ADS:
            raise NotImplementYetException()    
        elif self.io_type == IOType.MQTT:
            raise NotImplementYetException()    
        elif self.io_type == IOType.LORANODE:
            raise NotImplementYetException()    
        else:
            raise NotImplementYetException()    
    
    
    
    def open(self) -> None:
        if self.io_type == IOType.PCF8575:
            pass
        elif self.io_type == IOType.ADS:
            raise NotImplementYetException()    
        elif self.io_type == IOType.MQTT:
            raise NotImplementYetException()    
        elif self.io_type == IOType.LORANODE:
            raise NotImplementYetException()    
        else:
            raise NotImplementYetException()      
    
    def close(self) -> None:
        if self.io_type == IOType.PCF8575:
            pass
        elif self.io_type == IOType.ADS:
            raise NotImplementYetException()    
        elif self.io_type == IOType.MQTT:
            raise NotImplementYetException()    
        elif self.io_type == IOType.LORANODE:
            raise NotImplementYetException()    
        else:
            raise NotImplementYetException()      
        
        
    
groups_valves = db.Table('groups_valves',
                       Column('group_id', Integer, ForeignKey(Group.id), primary_key = True),
                        Column('valve_id', Integer, ForeignKey(Valve.id), primary_key = True))
    
class ADS(db.Model):
    
    __tablename__ = 'ads'
    
    __table_args__ = (
        UniqueConstraint("address", "pin", name='address_pin'),
      )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    address = Column(Enum(ADSAddress), nullable = False )
    pin = Column(Enum(ADSPin), nullable = False)
    
    def __repr__(self) -> str:
        return f"ADS {self.name} ({self.address.name}:{self.pin.name})"
    
    
class PCF8575(db.Model):
    
    __tablename__ = 'pcf8575'
    
    __table_args__ = (
        UniqueConstraint("address", "pin", name='address_pin'),
      )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    address = Column(Enum(PCF8575Address) )
    pin = Column(Enum(PCF8575Pin))
        
    def __init__(self,**kwargs):
        super(PCF8575, self).__init__(**kwargs)
        self.pcf_manager = PCF8575Manager.get_instance()
    
    def __repr__(self) -> str:
        return f"PCF {self.name} ({self.address.name}:{self.pin.name})"
    
    def set_input_pin(self):
        self.pcf_manager.set_input_pin(self.address, self.pin)

    def set_output_pin(self):
        self.pcf_manager.set_output_pin(self.address,self.pin)

    def set_output_value(self, value : bool):
        self.pcf_manager.set_output_value(self.address, self.pin, value)
    
    def get_pin_state(self) -> bool:
        return self.pcf_manager.get_pin_state(self.address, self.pin)    
    
    
class Mqtt(db.Model):
    __tablename__ = 'mqtt'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    identifier_name = Column(String(50), nullable=False, unique=True)
    server_ip = Column(String(50), nullable=False, default= 'localhost')
    server_port = Column(Integer, nullable=False, default= 1883 )
    server_username = Column(String(50))
    server_password = Column(String(50))
    in_topic = Column(String(50))
    out_topic = Column(String(50))
    
    def __repr__(self) -> str:
        return f"Mqtt {self.name} {self.identifier_name}"
    
class Lora(db.Model):
    __tablename__ = 'lora'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    device_id = Column(String(50), nullable=False)
    measurement = Column(String(50), nullable=False)
    port =  Column(Integer, nullable=False, default = 1)
    
    def __repr__(self) -> str:
        return f"Lora {self.name} {self.measurement}"
    
def randomColor():
    return random.choice(list(MyColor))

class Sensor(db.Model):
    __tablename__ = 'sensors'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    lora = relationship("Lora", uselist= False)
    lora_id = Column(Integer, ForeignKey('lora.id'))
    
    def __repr__(self) -> str:
        return f"Sensor {self.name}"
    
class ScheduleTask(db.Model):
    __tablename__ = 'schedule_tasks'
    id = Column(Integer, primary_key=True, autoincrement=True)
    plan_start_time = Column(DateTime)
    plan_duration = Column(Float)
    duration = Column(Float)
    start_time = Column(DateTime)
    finish_time = Column(DateTime)
    status = Column(Enum(TaskStatus), nullable = False, default = TaskStatus.INITIAL)
    created_date = Column(DateTime, default=datetime.now())
    task_type =  Column(Enum(TaskType), nullable = False)
    group = relationship("Group", uselist=False)
    
    group_id = Column(Integer, ForeignKey("groups.id"))
    
    
    
class Pump(db.Model):
    __tablename__ = 'pumps'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    pump_type = Column(Enum(PumpType), unique= True, nullable = True )

    pcf8575 = relationship("PCF8575", uselist=False, lazy = True)
    pcf_id = Column(Integer, ForeignKey("pcf8575.id"))
    
    def __init__(self,**kwargs):
        super(Pump, self).__init__(**kwargs)
        
        self.pcf8575.set_output_pin()
    
    def is_on(self) -> bool:
        return self.pcf8575.get_pin_state()
    
    def turn_on(self) -> None:
        self.pcf8575.set_output_value(True)
    
    def turn_off(self) -> None:
        self.pcf8575.set_output_value(False)
    
    
    
class MasterValve(db.Model):
    __tablename__ = 'master_valves'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    valve_type = Column(Enum(MasterValveType), unique= True, nullable = True )
    
    pcf8575 = relationship("PCF8575", uselist=False, lazy = True)
    pcf_id = Column(Integer, ForeignKey("pcf8575.id"))
    
    def __init__(self,**kwargs):
        super(MasterValve, self).__init__(**kwargs)
        
        self.pcf8575.set_output_pin()
    
    def is_on(self) -> bool:
        return self.pcf8575.get_pin_state()
    
    def turn_on(self) -> None:
        self.pcf8575.set_output_value(True)
    
    def turn_off(self) -> None:
        self.pcf8575.set_output_value(False)
        
        
class SeriesDisplayConfiguration(db.Model):
    __tablename__ = 'series_display_configurations'
    id = Column(Integer, primary_key=True, autoincrement=True)
    typec = Column(Enum(ChartType), default=ChartType.Scatter, nullable = False )
    mode = Column(Enum(ChartMode), default=ChartMode.Lines, nullable = False )
    name = Column(String(50), default="")
    color = Column(Enum(MyColor), default=randomColor , nullable = False )
    yaxis = Column(Enum(ChartYAxis), default = ChartYAxis.yaxis1, nullable = False )
     
    sensor = relationship("Sensor", uselist=False)
    sensor_id = Column(Integer, ForeignKey("sensors.id"))
    
    def __repr__(self) -> str:
        return f"Series Display {self.name}"

        
class Chart(db.Model):
    __tablename__ = 'charts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    active = Column(Boolean, nullable=False, default= True )
    title = Column(String(100), default= "", nullable=False)
    yaxis_title = Column(String(100), default= "", nullable=True)
    yaxis2_title = Column(String(100), default = "", nullable=True)
    
    has_series_displays = db.relationship('SeriesDisplayConfiguration', secondary='charts_series_display_configurations', lazy = True, 
                                            backref = backref('in_charts', lazy = True))

    def __repr__(self) -> str:
        return f"Chart {self.id} {self.title}"


charts_series_display_configurations = db.Table('charts_series_display_configurations',
                       Column('chart_id', Integer, ForeignKey(Chart.id), primary_key = True),
                        Column('series_display_configuration_id', Integer, ForeignKey(SeriesDisplayConfiguration.id), primary_key = True))




import itertools
def init_database_default():        #initial database with value by default for easy testing
    admin = User(name='Admin', username= 'admin', password = '1234', user_role = UserRole.ADMIN)
    db.session.add(admin)
    
    pcf_list = []
    for address, pin in itertools.product(PCF8575Address, PCF8575Pin):
        pcf = PCF8575(name=f"{address.value}-{pin.value} ", address= address, pin= pin)
        db.session.add(pcf)
        pcf_list.append(pcf)
    
    ads_list = []    
    for address, pin in itertools.product(ADSAddress, ADSPin):
        ads = ADS(name=address.name, address=address, pin= pin)
        db.session.add(ads)
        ads_list.append(ads)
    
    group_id_list = [i for i in range(1, 10 + 1)]
    valve_id_start = 1
    for group_id in group_id_list:
        m_group = Group(name=f"Group {group_id}", description = f"This is group {group_id}")
        
        for valve_id in  range(valve_id_start, valve_id_start + 5  ):
            m_valve = Valve(name=f'Valve {valve_id}', description = f"This is valve {valve_id}" )
            m_valve.pcf8575 = pcf_list[valve_id - 1 ]
            
            m_group.has_valves.append(m_valve)
        valve_id_start += 5 
        db.session.add(m_group)
        

    for index, pumpType in enumerate(PumpType) :
        m_pump = Pump(name=f"Pump {pumpType.name}", pump_type= pumpType, pcf8575 = pcf_list[valve_id_start+ index])
        db.session.add(m_pump)
        
    valve_id_start += len(PumpType)
    
    for index, valve_type in enumerate(MasterValveType):
        m_master_valve = MasterValve(name=f'MasterValve {valve_type.name}', valve_type = valve_type, pcf8575 = pcf_list[valve_id_start+ index] )
        db.session.add(m_master_valve)
        
    for i in range (1, 9):
        lora_temp0 = Lora(name=f"Dev {i} Temp0", device_id= f"000000000000000{i}",measurement= 'device_frmpayload_data_temp0')
        sensor_temp0 = Sensor(name=f"Dev {i} Temp0" )
        sensor_temp0.lora = lora_temp0
        series_display_temp0 = SeriesDisplayConfiguration(name=f"Dev {i} Temp0")
        series_display_temp0.sensor = sensor_temp0
        db.session.add(series_display_temp0)
        
        lora_temp3 = Lora(name=f"Dev {i} Temp3", device_id= f"000000000000000{i}",measurement= 'device_frmpayload_data_temp3')
        sensor_temp3 = Sensor(name=f"Dev {i} Temp3" )
        sensor_temp3.lora = lora_temp3
        series_display_temp3 = SeriesDisplayConfiguration(name=f"Dev {i} Temp3")
        series_display_temp3.sensor = sensor_temp3
        db.session.add(series_display_temp3)
        
        lora_ec_pore0 = Lora(name=f"Dev {i} EC Pore 0", device_id= f"000000000000000{i}",measurement= 'device_frmpayload_data_ec_pore0')
        sensor_ec_pore0 = Sensor(name=f"Dev {i} EC Pore 0" )
        sensor_ec_pore0.lora = lora_ec_pore0
        series_display_pore0 = SeriesDisplayConfiguration(name=f"Dev {i} EC Pore")
        series_display_pore0.sensor = sensor_ec_pore0
        db.session.add(series_display_pore0)
        
        lora_soil0 = Lora(name=f"Dev {i} Soil 0", device_id= f"000000000000000{i}",measurement= 'device_frmpayload_data_soil_vwc0')
        sensor_soil0 = Sensor(name=f"Dev {i} Soil 0" )
        sensor_soil0.lora = lora_soil0
        series_display_soil0 = SeriesDisplayConfiguration(name=f"Dev {i} Soil0")
        series_display_soil0.sensor = sensor_soil0
        db.session.add(series_display_soil0)
        
        lora_soiless0 = Lora(name=f"Dev {i} Soiless 0", device_id= f"000000000000000{i}",measurement= 'device_frmpayload_data_soiless_vwc0')
        sensor_soiless0 = Sensor(name=f"Dev {i} Soiless 0" )
        sensor_soiless0.lora = lora_soiless0
        series_display_soiless0 = SeriesDisplayConfiguration(name=f"Dev {i} Soiless0")
        series_display_soiless0.sensor = sensor_soiless0
        db.session.add(series_display_soiless0)   

        lora_water_potential = Lora(name=f"Dev {i} Water Potenial", device_id= f"000000000000000{i}",measurement= 'device_frmpayload_data_water_potential')
        sensor_water_potential = Sensor(name=f"Dev {i} Water Potential" )
        sensor_water_potential.lora = lora_water_potential
        series_display_water_potential = SeriesDisplayConfiguration(name=f"Dev {i} Water Potential")
        series_display_water_potential.sensor = sensor_water_potential
        db.session.add(series_display_water_potential)   
        
        lora_battery = Lora(name=f"Dev {i} Battery", device_id= f"000000000000000{i}",measurement= 'device_frmpayload_data_battery')
        sensor_lora_battery = Sensor(name=f"Dev {i} Battery" )
        sensor_lora_battery.lora = lora_battery
        series_display_battery = SeriesDisplayConfiguration(name=f"Dev {i} Baterry")
        series_display_battery.sensor = sensor_lora_battery
        db.session.add(series_display_battery)   
    
        chart_temp0 = Chart(title=series_display_battery.name)
        chart_temp0.has_series_displays.append( series_display_battery)
        db.session.add(chart_temp0)
        
        # chart_water_potential = Chart(title=sensor_water_potential.name)
        # chart_water_potential.sensor = sensor_water_potential
        # db.session.add(chart_water_potential)
        
        # chart_water_potential = Chart(title=sensor_ec_pore0.name)
        # chart_water_potential.sensor = sensor_ec_pore0
        # db.session.add(chart_water_potential)
    
    


if __name__ == "__main__":
    db.drop_all()
    db.session.commit()
    db.create_all()
    init_database_default()
    # valve = ValveModel(name="Test Valve")
    # db.session.add(valve)
    db.session.commit()


