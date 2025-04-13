"""
Configuration settings for the AGV scheduling system.
"""


class PathfindingConfig:
    """Configuration for pathfinding algorithms"""
    DEFAULT_ALGORITHM = "dijkstra"  # Used in Algorithm 1 for finding shortest route
    INFINITY = float('inf')  # Value used for unreachable nodes


class AGVConfig:
    """Configuration for AGV operations"""
    DEFAULT_SPEED = 1.0  # meters per second, as specified in algorithms-pseudocode.tex
