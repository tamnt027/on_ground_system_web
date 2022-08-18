
from abc import ABC, abstractmethod
import sys
from pathlib import Path
from time import sleep
parent = str(Path(__file__).parent.parent.absolute())
sys.path.append(parent)

from my_logger import logging
from my_enum import PCF8575Address, PCF8575Pin, PinMode
from my_exception import FileJsonException
import os, json

class PCFInterface(ABC):
    def __init__(self, address : PCF8575Address):
        self.address = address
        self.input_mask = 0xFFFF  # default all is input pin
    
    @abstractmethod
    def set_input_pin(self, pin : PCF8575Pin):
        pass
    
    @abstractmethod
    def set_output_pin(self, pin : PCF8575Pin):
        pass
    
    @abstractmethod
    def set_output_value(self, pin : PCF8575Pin, value : bool):
        pass    
    
    @abstractmethod
    def get_pin_state(self, pin : PCF8575Pin) -> bool:
        pass

    @abstractmethod
    def is_input_pin(self, pin :PCF8575Pin) -> bool:
        pass

class PCFBoardEmu(PCFInterface):
    
    DATA_FILE = 'pcf_board_emu_data.json'
    PIN_MODE = 'pin_mode'
    VALUE = 'value'
    
    def __init__(self, address : PCF8575Address):
        super().__init__(address)
        self._generate_board_dict()
        self._save_to_file(save_all=True)

             
    def _generate_board_dict(self):         # generate default value for _board_dict
        self._board_dict = {}
        for pin in PCF8575Pin:
            self._board_dict[pin.name] = {PCFBoardEmu.PIN_MODE : 1, PCFBoardEmu.VALUE : 0}
        
        logging.debug(f"_board_dict at {self.address.name} has value {self._board_dict}")
        
    def _save_to_file(self, save_all : bool = False):
        try:
            if os.path.exists(PCFBoardEmu.DATA_FILE):
                try:
                    old_json_content = self._load_from_file()  # load current content for file, only update OUT pin_mode only
                    if self.address.name in old_json_content:
                        for pin in PCF8575Pin:
                            is_input = bool(self.input_mask & 1 << pin.value) 
                            if is_input == False or save_all == True:
                                old_json_content[self.address.name][pin.name][PCFBoardEmu.PIN_MODE] = self._board_dict[pin.name][PCFBoardEmu.PIN_MODE]
                                old_json_content[self.address.name][pin.name][PCFBoardEmu.VALUE] = self._board_dict[pin.name][PCFBoardEmu.VALUE]
                    else:
                        old_json_content[self.address.name] = self._board_dict
                        
                    with open(PCFBoardEmu.DATA_FILE, "w") as out_file:     # update json content to file
                        json.dump(old_json_content, out_file,  indent=4)
                        
                except:
                    logging.error(f"File {PCFBoardEmu.DATA_FILE} content is invalid.")
                    raise FileJsonException("invalid content")
            else:
                raise FileJsonException("not exist")
            
        except FileJsonException as e:
            logging.info(f"File {PCFBoardEmu.DATA_FILE} not exists or invalid ({e}), creating new one.")
            with open(PCFBoardEmu.DATA_FILE, "w") as out_file:
                save_json_content = {}
                save_json_content[self.address.name] = self._board_dict
                json.dump(save_json_content, out_file,  indent=4)
                
    
    def _load_from_file(self) :
        if os.path.exists(PCFBoardEmu.DATA_FILE):
            try:
                with open(PCFBoardEmu.DATA_FILE, "r") as in_file:
                    json_content = json.load(in_file)
                    return json_content
            except :
                logging.error(f"Cannot read file {PCFBoardEmu.DATA_FILE}.")
                return {}
                
        else:   # not exists DATA_FILE
            logging.info(f"File {PCFBoardEmu.DATA_FILE} not exists.")
            return {}
            
    def __repr__(self):
        return "PCFBoardEmu(address=%s)" % (self.address.name)
    
    def set_input_pin(self, pin: PCF8575Pin):
        self.input_mask = self.input_mask | 1 << pin.value 
        self._board_dict[pin.name][PCFBoardEmu.PIN_MODE] = 1
    
    def set_output_pin(self, pin: PCF8575Pin):
        self.input_mask = self.input_mask & ~( 1<< pin.value)
        self._board_dict[pin.name][PCFBoardEmu.PIN_MODE] = 0
    
    def set_output_value(self, pin: PCF8575Pin, value: bool):
        logging.debug(f"{self.__repr__()} set pin {pin.name} to {value} ")
        
        input_pin = bool(self.input_mask & 1 << pin.value)    #make sure not input mode
        if input_pin == True:
            logging.warning(f"{self.__repr__()} cannot set output value because pin {pin.name} is in input mode")
            return 
        
        self._board_dict[pin.name][PCFBoardEmu.VALUE] = int(value)
        self._save_to_file()
    
    def get_pin_state(self, pin: PCF8575Pin)  -> bool:
        input_pin = bool(self.input_mask & 1 << pin.value)    #make sure not input mode
        if input_pin == True:   # for input pin state, need to load value from file
            old_json_content = self._load_from_file()  # load current content for file, only update INPUT pin_mode only
            if self.address.name in old_json_content:
                is_input = bool(self.input_mask & 1 << pin.value) 
                if is_input == True:
                    self._board_dict[pin.name][PCFBoardEmu.VALUE] = old_json_content[self.address.name][pin.name][PCFBoardEmu.VALUE] 
            
        return self._board_dict[pin.name][PCFBoardEmu.VALUE]
    
    def is_input_pin(self, pin :PCF8575Pin) -> bool:
        return bool(self.input_mask & 1 << pin.value)
        
    
class PCFBoard(PCFInterface):
    
    def __init__(self, address : PCF8575Address):
        super().__init__(address)
        self._bus_no = 1
        try:
            import smbus
            self.bus = smbus.SMBus(self._bus_no)
            self._write_a_word(self.input_mask)
        except:
            logging.exception(f"Init {self.__repr__()} failed.")
            self.bus = None

    def __repr__(self):
        return "PCFBoard(address=%s)" % (self.address.name)
    
     
    def _write_a_word(self, a_word):
        try:
            if self.bus:
                self.bus.write_byte_data(self.address.value, a_word & 0xff, (a_word >> 8) & 0xff)
        except:
            logging.exception(f"{self.__repr__()} write a word failed.")
            
            
    def _read_word_data(self):
        try: 
            word = self.bus.read_word_data(self.address, 0)
            return word
        except:
            logging.exception(f"{self.__repr__()} read a word failed.")
            word = 0x0000
            return word
    
    
    def set_input_pin(self, pin : PCF8575Pin):
        self.input_mask = self.input_mask | 1 << pin.value                   # update input mask.
        current_state = self._read_word_data()             # read current state and force all input pins to true
        new_state = current_state | self.input_mask
        self._write_a_word(new_state)

    def is_input_pin(self, pin :PCF8575Pin) -> bool:
        return bool(self.input_mask & 1 << pin.value)

    def set_output_pin(self, pin : PCF8575Pin):
        self.input_mask = self.input_mask & ~( 1<< pin.value)
        
        
    def set_output_value(self, pin: PCF8575Pin, value: bool):
        logging.debug(f"{self.__repr__()} set pin {pin.name} to {value} ")
        
        input_pin = bool(self.input_mask & 1 << pin.value)    #make sure not input mode
        if input_pin == True:
            logging.warning(f"{self.__repr__()} cannot set output value because pin {pin.name} is in input mode")
            return 
        
        current_state = self._read_word_data()
        bit = 1 << pin.value
        new_state = current_state | bit if value else current_state & (~bit)
        self._write_a_word(new_state)

    def get_pin_state(self, pin: PCF8575Pin) -> bool:
        state = self._read_word_data()
        return bool(state & 1 << pin.value)
    
    


class PCF8575Manager:
    __instance = None

    @staticmethod
    def get_instance():
        if PCF8575Manager.__instance == None:
            PCF8575Manager.__instance = PCF8575Manager()
        return PCF8575Manager.__instance

    def __init__(self) -> None:

        if PCF8575Manager.__instance != None:
            raise Exception(f"This is a singleton!")
        else:
            PCF8575Manager.__instance = self  
       
        self.pcf8575_board_list = self._get_board_list()
    
    def _get_board_list(self):
        board_list = {}
        for address in PCF8575Address:
            board = PCFBoardEmu(address)
            board_list[address.name] = board
    
        return board_list
        
    def _get_board(self, address : PCF8575Address) -> PCFInterface:
        board = self.pcf8575_board_list[address.name]
        return board
    
    def set_pin_mode(self, address : PCF8575Address, pin : PCF8575Pin, mode : PinMode):
        board = self._get_board(address)
        if mode == PinMode.INPUT:
            board.set_input_pin(pin)
        elif mode == PinMode.OUTPUT:
            board.set_output_pin(pin)
          
          
    def is_input_pin(self, address : PCF8575Address, pin : PCF8575Pin) -> bool:  
        board = self._get_board(address)
        return board.is_input_pin(pin=pin) 

    def set_input_pin(self,  address : PCF8575Address, pin : PCF8575Pin):
        board = self._get_board(address)
        board.set_input_pin(pin=pin) 

    def set_output_pin(self,  address : PCF8575Address, pin : PCF8575Pin):
        board = self._get_board(address)
        board.set_output_pin(pin=pin)

    def set_output_value(self,  address : PCF8575Address, pin : PCF8575Pin, value : bool):
        board = self._get_board(address)
        board.set_output_value(pin=pin, value=value)    
    
    def get_pin_state(self,  address : PCF8575Address, pin : PCF8575Pin) -> bool:
        board = self._get_board(address)
        return board.get_pin_state(pin=pin)    


if __name__ == '__main__':
    pcf_manager = PCF8575Manager.get_instance()
    while True:
        pin_state = pcf_manager.get_pin_state(PCF8575Address.ADD0x20, PCF8575Pin.P01)
        sleep(1)
        # pcf_manager.set_output_pin(PCF8575Address.ADD0x20, PCF8575Pin.P02)
        # pcf_manager.set_output_value(PCF8575Address.ADD0x20, PCF8575Pin.P02, 1)
        print(f"Pin state {pin_state}")