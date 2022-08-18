



from abc import ABC, abstractmethod
from datetime import datetime
from models import ScheduleTask
import threading
from init import db
from my_enum import MasterValveType, PumpType, TaskStatus
from pcf8575_manager import PCF8575Manager
from utils import get_master_valve, get_pump
import time

class ProcessIF(ABC):
    def __init__(self) -> None:
        self.is_running = False
        self.is_force_stop = False

    def start(self):
        self.thread = threading.Thread(target=self._task_operation)
        self.thread.start()
    
    def stop(self):
        if self.thread and self.is_running:
            self.is_force_stop = True
            self.thread.join()
            self.is_running = False
        pass
    
    def on_running(self):
        return self.is_running
    
    @abstractmethod
    def _task_body(self):
        pass
    
    def _task_operation(self):
        self.is_running = True
        self.is_force_stop = False
        
        self._task_body()
        
        self.is_running = False
        
        

class IrrigationProcess(ProcessIF):
    pass
    def __init__(self, schedule_task : ScheduleTask) -> None:
        super().__init__()
        self.schedule_task = schedule_task
        self.pump_type = PumpType.BORE_1
        self.master_valve_type = MasterValveType.MASTER_1
        self.pcf_manager = PCF8575Manager.get_instance()
        
    def _post_task(self):
        self.pump.turn_off()
        self.master_valve.turn_off()
        self.schedule_task.group.close_valves()
        
        self.schedule_task.finish_time = datetime.now()
        self.schedule_task.duration = time.time() - self.start_time
        self.schedule_task.status = TaskStatus.DONE
        db.session.commit() 
            
         
    def _task_body(self):
        try:
            self.start_time = time.time()
            self.schedule_task.start_time = datetime.now()
            self.schedule_task.status = TaskStatus.RUNNING
            db.session.commit()
            self.pump = get_pump(self.pump_type)  
            self.master_valve = get_master_valve(self.master_valve_type)     

            while self.is_force_stop == False and time.time() - self.start_time < self.schedule_task.plan_duration:
                self.master_valve.turn_on()
                self.schedule_task.group.open_valves()
                self.pump.turn_on()
            
            self._post_task()
        except Exception as e:
            self._post_task()
            
        
        
        return super()._task_body()
        
        
class ProcessManager:
    
    def __init__(self) -> None:
        pass