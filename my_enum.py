from enum import Enum as MyEnum


class UserRole(MyEnum):
    ADMIN = 1
    USER = 2
    
    
class ADSAddress(MyEnum):
    ADD0x48 = 0x48
    ADD0x49 = 0x49
    ADD0x4A = 0x4A
    ADD0x4B = 0x4B
    
    
class ADSPin(MyEnum):
    A0 = 0
    A1 = 1
    A2 = 2
    A3 = 3
    
    
class PCF8575Address(MyEnum):
    ADD0x20 = 0x20
    ADD0x21 = 0x21
    ADD0x22 = 0x22
    ADD0x23 = 0x23
    ADD0x24 = 0x24
    ADD0x25 = 0x25
    ADD0x26 = 0x26
    ADD0x27 = 0x27
    
    
class PCF8575Pin(MyEnum):
    P00 = 15
    P01 = 14
    P02 = 13
    P03 = 12
    P04 = 11
    P05 = 10
    P06 = 9
    P07 = 8
    P10 = 7
    P11 = 6
    P12 = 5
    P13 = 4
    P14 = 3
    P15 = 2
    P16 = 1
    P17 = 0
    
class PinMode(MyEnum):
    OUTPUT = 0
    INPUT = 1    

class IOType(MyEnum):
    ADS = 1
    PCF8575 = 2
    MQTT = 3
    LORANODE = 4
    
    
class TaskStatus(MyEnum):
    INITIAL = 0
    RUNNING = 1
    DONE = 2
    CANCEL = 3
    
    
class PumpType(MyEnum):
    BORE_1 = 0
    BORE_2 = 1
    HYDRO_1 = 2
    
class MasterValveType(MyEnum):
    MASTER_1 = 0
    MASTER_2 = 1
    MASTER_3 = 2
    MASTER_4 = 3
    
    
class TaskType(MyEnum):
    IRRIGATION_GROUND = 0
    IRRIGATION_HYDROPONIC = 1
    TO_RAW_WATER = 2
    TO_BATCH_TANK = 3
    
    
class MyColor(MyEnum):
    
    Pink = '#FFC0CB'
    Crimson = '#DC143C'
    Red = '#FF0000'
    Maroon = '#800000'
    Brown = '#A52A2A'
    MistyRose = '#FFE4E1'
    Salmon = '#FA8072'
    Coral = '#FF7F50'
    OrangeRed = '#FF4500'
    Gold = '#FFD700'
    Ivory = '#FFFFF0'
    Yellow = '#FFFF00'
    Olive = '#808000'
    YellowGreen = '#9ACD32'
    LawnGreen = '#7CFC00'
    Chartreuse = '#7FFF00'
    Lime = '#00FF00'
    Green = '#008000'
    Aquamarine = '#7FFFD4'
    Turquoise = '#40E0D0'	
    Azure = '#F0FFFF'
    Cyan = '#00FFFF'	
    Teal = '#008080'
    Lavender = '#E6E6FA'
    Blue = '#0000FF'	
    Navy = '#000080'	
    BlueViolet = '#8A2BE2'
    Indigo = '#4B0082'
    DarkViolet = '#9400D3'
    Plum = '#DDA0DD	'	
    Magenta	 = '#FF00FF'	
    Purple = '#A020F0'	
    Tan = '#D2B48C'		
    Beige = '#F5F5DC'		
    LightGray	= '#D3D3D3'	
    Silver	= '#C0C0C0'	
    DarkGray = '#A9A9A9'	
    Black = '#000000'	