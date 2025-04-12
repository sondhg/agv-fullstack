from enum import IntEnum

class AGVState(IntEnum):
    """AGV states as defined in the paper"""
    IDLE = 0
    MOVING = 1
    WAITING = 2

class ErrorMessages:
    """Error messages used throughout the application"""
    NO_ORDERS = "No orders available to generate schedules."
    INVALID_MAP_DATA = "Map data is incomplete or missing."
    INVALID_ALGORITHM = "Invalid pathfinding algorithm specified."
    NO_SCHEDULES = "No schedules were generated. Check the input data."
    BULK_DELETE_NO_IDS = "No schedule IDs provided for deletion."

class SuccessMessages:
    """Success messages used throughout the application"""
    SCHEDULES_GENERATED = "Schedules generated successfully."
    SCHEDULE_DELETED = "Schedule {} deleted successfully."
    SCHEDULES_DELETED = "{} schedules deleted successfully."

class DefaultValues:
    """Default values used in the application"""
    EMPTY_TRAVELING_INFO = {"v_c": None, "v_n": None, "v_r": None}
    DEFAULT_ALGORITHM = "dijkstra"
    DEFAULT_INSTRUCTION_SET = "[]" 