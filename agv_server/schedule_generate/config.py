"""
Configuration settings for the AGV scheduling system.
"""

class PathfindingConfig:
    """Configuration for pathfinding algorithms"""
    AVAILABLE_ALGORITHMS = ["dijkstra", "a_star", "floyd_warshall"]
    DEFAULT_ALGORITHM = "dijkstra"
    MAX_PATH_LENGTH = 1000  # Maximum allowed path length
    INFINITY = float('inf')  # Value used for unreachable nodes

class AGVConfig:
    """Configuration for AGV operations"""
    DEFAULT_SPEED = 1.0  # meters per second
    SAFETY_DISTANCE = 2.0  # meters
    MAX_WAITING_TIME = 300  # seconds
    MAX_SPARE_POINTS = 5  # Maximum number of spare points per AGV

class DeadlockConfig:
    """Configuration for deadlock detection and resolution"""
    MAX_DEADLOCK_RESOLUTION_ATTEMPTS = 3
    DEADLOCK_CHECK_INTERVAL = 5  # seconds
    MAX_LOOP_SIZE = 10  # Maximum number of AGVs in a loop deadlock

class DatabaseConfig:
    """Configuration for database operations"""
    BATCH_SIZE = 100  # Batch size for bulk operations
    MAX_CONNECTIONS = 20
    TIMEOUT = 30  # seconds

class LoggingConfig:
    """Configuration for logging"""
    ENABLED = True
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = "agv_scheduler.log"

class CacheConfig:
    """Configuration for caching"""
    ENABLED = True
    TIMEOUT = 300  # seconds
    MAX_ENTRIES = 1000 