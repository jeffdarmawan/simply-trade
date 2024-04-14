from enum import Enum

class Status(Enum):
    Active = 1
    Inactive = 2
    Stop = 3

class Models(Enum): 
    OneMin = 1
    FiveMin = 2
    FifteenMin = 3
    OneHour = 4
