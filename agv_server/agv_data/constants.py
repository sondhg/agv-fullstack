"""Constants used for AGV data and scheduling functionality."""


class DirectionChangeOptions:
    """Options for direction changes when AGV reaches a node and is in MOVING state"""
    STRAIGHT = 0  # Go straight
    REVERSE = 1  # Reverse
    LEFT = 2  # Turn left
    RIGHT = 3  # Turn right


class ErrorMessages:
    """Error messages used throughout the application"""
    NO_ORDERS = "No orders available to dispatch."
    INVALID_MAP_DATA = "Map data is incomplete or missing."
    INVALID_ALGORITHM = "Invalid pathfinding algorithm specified."


class SuccessMessages:
    """Success messages used throughout the application"""
    ORDER_PROCESSED = "Order {} processed successfully."
    ORDERS_PROCESSED = "{} orders processed successfully."


class DefaultValues:
    """Default values used in the application"""
    DEFAULT_ALGORITHM = "dijkstra"
    DEFAULT_PATH = "[]"
