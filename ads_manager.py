

from abc import ABC, abstractmethod
import sys
from pathlib import Path
from time import sleep
parent = str(Path(__file__).parent.parent.absolute())
sys.path.append(parent)

from my_logger import logging
from my_enum import ADSAddress, ADSPin
from my_exception import FileJsonException
import os, json

class ADSInterface(ABC):
    def __init__(self, address : ADSAddress):
        self.address = address
        
        
    # Choose a gain of 1 for reading voltages from 0 to 4.09V.
    # Or pick a different gain to change the range of voltages that are read:
    #  - 2/3 = +/-6.144V
    #  -   1 = +/-4.096V
    #  -   2 = +/-2.048V
    #  -   4 = +/-1.024V
    #  -   8 = +/-0.512V
    #  -  16 = +/-0.256V       
    @abstractmethod
    def get_pin_value(self, pin : ADSPin, gain = 1) -> int:
        pass
    

class ADSBoardEmu(ADSInterface):
    
    DATA_FILE = 'ads_board_emu_data.json'
    VALUE = 'value'
    
    def __init__(self, address : ADSAddress):
        super().__init__(address)
        self._generate_board_dict()
        self._save_to_file()

             
    def _generate_board_dict(self):         # generate default value for _board_dict
        self._board_dict = {}
        for pin in ADSPin:
            self._board_dict[pin.name] = { ADSBoardEmu.VALUE : 0}
        
        logging.debug(f"_board_dict at {self.address.name} has value {self._board_dict}")
        
    def _save_to_file(self):
        try:
            if os.path.exists(ADSBoardEmu.DATA_FILE):
                try:
                    old_json_content = self._load_from_file()  # load current content for file, only update OUT pin_mode only
                    if self.address.name in old_json_content:
                        for pin in ADSPin:
                            old_json_content[self.address.name][pin.name][ADSBoardEmu.VALUE] = self._board_dict[pin.name][ADSBoardEmu.VALUE]
                    else:
                        old_json_content[self.address.name] = self._board_dict
                        
                    with open(ADSBoardEmu.DATA_FILE, "w") as out_file:     # update json content to file
                        json.dump(old_json_content, out_file,  indent=4)
                        
                except:
                    logging.error(f"File {ADSBoardEmu.DATA_FILE} content is invalid.")
                    raise FileJsonException("invalid content")
            else:
                raise FileJsonException("not exist")
            
        except FileJsonException as e:
            logging.info(f"File {ADSBoardEmu.DATA_FILE} not exists or invalid ({e}), creating new one.")
            with open(ADSBoardEmu.DATA_FILE, "w") as out_file:
                save_json_content = {}
                save_json_content[self.address.name] = self._board_dict
                json.dump(save_json_content, out_file,  indent=4)
                
    
    def _load_from_file(self) :
        if os.path.exists(ADSBoardEmu.DATA_FILE):
            try:
                with open(ADSBoardEmu.DATA_FILE, "r") as in_file:
                    json_content = json.load(in_file)
                    return json_content
            except :
                logging.error(f"Cannot read file {ADSBoardEmu.DATA_FILE}.")
                return {}
                
        else:   # not exists DATA_FILE
            logging.info(f"File {ADSBoardEmu.DATA_FILE} not exists.")
            return {}
        
        
    def get_pin_value(self, pin : ADSPin, gain = 1) -> int:
        old_json_content = self._load_from_file()  # load current content for file, only update INPUT pin_mode only
        if self.address.name in old_json_content:
            self._board_dict[pin.name][ADSBoardEmu.VALUE] = old_json_content[self.address.name][pin.name][ADSBoardEmu.VALUE] 
            
        return self._board_dict[pin.name][ADSBoardEmu.VALUE]
            
    def __repr__(self):
        return "ADSBoardEmu(address=%s)" % (self.address.name)
    

        
    
class ADSBoard(ADSInterface):
    
    def __init__(self, address : ADSAddress):
        super().__init__(address)
        try:
            import Adafruit_ADS1x15                     # https://github.com/adafruit/Adafruit_Python_ADS1x15
            self.adc  = Adafruit_ADS1x15.ADS1015(address= self.address.value, busnum=1)
        except:
            logging.exception(f"Init {self.__repr__()} failed.")

    def __repr__(self):
        return "ADSBoard(address=%s)" % (self.address.name)
    
    def get_pin_value(self, pin : ADSPin, gain = 1) -> int:
        return self.adc.read_adc(pin.value, gain=gain)
    
    
class ADSManager:
    __instance = None

    @staticmethod
    def get_instance():
        if ADSManager.__instance == None:
            ADSManager.__instance = ADSManager()
        return ADSManager.__instance

    def __init__(self) -> None:

        if ADSManager.__instance != None:
            raise Exception(f"This is a singleton!")
        else:
            ADSManager.__instance = self  
       
        self.ads_board_list = self._get_board_list()
    
    def _get_board_list(self):
        board_list = {}
        for address in ADSAddress:
            board = ADSBoardEmu(address)
            board_list[address.name] = board
    
        return board_list
        
    def _get_board(self, address : ADSAddress) -> ADSInterface:
        board = self.ads_board_list[address.name]
        return board
    
    def get_pin_value(self, address : ADSAddress, pin : ADSPin, gain = 1) -> int:
        board = self._get_board(address)
        return board.get_pin_value(pin, gain=gain)


if __name__ == '__main__':
    ads_manager = ADSManager.get_instance()
    while True:
        pin_state = ads_manager.get_pin_value(ADSAddress.ADD0x48, ADSPin.A0)
        print(f"Pin value {pin_state}")
        sleep(1)