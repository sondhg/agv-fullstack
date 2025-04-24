"""Constants used for AGV data and scheduling functionality."""
# AGV States from Algorithm 2 (SA^i)
AGV_STATE_IDLE = 0    # No mission to execute
AGV_STATE_MOVING = 1  # On way to next reserved point
AGV_STATE_WAITING = 2  # Stopped at current point


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
    ORDER_PROCESSED = "Order {} processed successfully."
    ORDERS_PROCESSED = "{} orders processed successfully."


class DefaultValues:
    """Default values used in the application"""
    DEFAULT_ALGORITHM = "dijkstra"
    DEFAULT_PATH = "[]"
