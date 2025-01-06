from enum import Enum


class PrintControllerState(Enum):
    IDLE = 0
    PRINTING = 1


class StateControllerState(Enum):
    INIT = 0
    PREPARE = 1
    EXPOSE = 2
    GAP = 3
    WASH = 4
    CLOSE = 5
    REST = 6
