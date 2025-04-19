from enum import IntEnum
from agv_data.models import AGV_STATE_IDLE, AGV_STATE_MOVING, AGV_STATE_WAITING

class AGVState:
    """AGV states as defined in the paper"""
    IDLE = AGV_STATE_IDLE
    MOVING = AGV_STATE_MOVING
    WAITING = AGV_STATE_WAITING

class ErrorMessages:
    """Error messages used throughout the application"""
    NO_ORDERS = "No orders available to generate schedules."
    INVALID_MAP_DATA = "Map data is incomplete or missing."
    INVALID_ALGORITHM = "Invalid pathfinding algorithm specified."
    NO_SCHEDULES = "No schedules could be generated"
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