"""Constants used in the map_data module."""


class MapConstants:
    """Map-related constants"""

    NO_CONNECTION = 10000  # Value indicating no direct connection between nodes
    DEFAULT_NODE_COUNT = 0
    NODE_INDEX_OFFSET = 1  # Offset to convert 0-based indices to 1-based node numbers


class ErrorMessages:
    """Error messages used in the map_data module"""

    INCOMPLETE_MAP = "Map data is incomplete or missing."
    INVALID_DATA = "Invalid data format provided."
    IMPORT_ERROR = "Error importing map data: {}"
    DELETE_ERROR = "Error deleting map data: {}"
    INVALID_DIRECTION = "Invalid direction value. Must be between 1 and 4."


class LogMessages:
    """Logging messages used in the map_data module"""

    IMPORT_CONNECTIONS = "Imported connections: {}"
    IMPORT_DIRECTIONS = "Imported directions: {}"
    DELETE_SUCCESS = "All map data deleted successfully."
    DELETE_ERROR = "Error deleting map data: {}"
