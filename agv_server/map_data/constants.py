"""Constants used in the map_data module."""

class MapConstants:
    """Map-related constants"""
    NO_CONNECTION = 10000  # Value indicating no direct connection between nodes
    DEFAULT_NODE_COUNT = 0
    NODE_INDEX_OFFSET = 1  # Offset to convert 0-based indices to 1-based node numbers

class DirectionConstants:
    """Cardinal direction constants for AGV movement"""
    NORTH = 1
    EAST = 2
    SOUTH = 3
    WEST = 4
    DIRECTION_CHOICES = [
        (NORTH, 'North'),
        (EAST, 'East'),
        (SOUTH, 'South'),
        (WEST, 'West'),
    ]

class ErrorMessages:
    """Error messages used in the map_data module"""
    INCOMPLETE_MAP = "Map data is incomplete or missing."
    INVALID_DATA = "Invalid data format provided."
    IMPORT_ERROR = "Error importing map data: {}"
    DELETE_ERROR = "Error deleting map data: {}"
    INVALID_DIRECTION = "Invalid direction value. Must be between 1 and 4."

class SuccessMessages:
    """Success messages used in the map_data module"""
    CONNECTIONS_IMPORTED = "Connection data imported successfully"
    DIRECTIONS_IMPORTED = "Direction data imported successfully"
    DATA_DELETED = "All map data deleted successfully"

class LogMessages:
    """Logging messages used in the map_data module"""
    IMPORT_CONNECTIONS = "Imported connections: {}"
    IMPORT_DIRECTIONS = "Imported directions: {}"
    DELETE_SUCCESS = "All map data deleted successfully."
    DELETE_ERROR = "Error deleting map data: {}" 