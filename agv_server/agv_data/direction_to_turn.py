from map_data.models import Direction
from .models import Agv

# Extract cardinal direction constants directly from the Direction model
NORTH, EAST, SOUTH, WEST = Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST
# Extract direction change constants directly from the Agv model
TURN_RIGHT, TURN_LEFT, GO_STRAIGHT, TURN_AROUND = Agv.TURN_RIGHT, Agv.TURN_LEFT, Agv.GO_STRAIGHT, Agv.TURN_AROUND


def get_direction(from_node, to_node):
    """
    Get the cardinal direction from one node to another.

    Args:
        from_node (int): The starting node.
        to_node (int): The destination node.

    Returns:
        int: The direction from `from_node` to `to_node`:
             NORTH, EAST, SOUTH, WEST.
             Returns None if no direction is found in the `Direction` model.
    """
    try:
        return Direction.objects.get(node1=from_node, node2=to_node).direction
    except Direction.DoesNotExist:
        return None  # Return None if no direction is found


def get_action(prev_node, current_node, next_node):
    """
    Determine the action (direction change) based on three consecutive nodes.

    Args:
        prev_node (int): The previous node in the path.
        current_node (int): The current node in the path.
        next_node (int): The next node in the path.

    Returns:
        int: The action the AGV should take at the `current_node`:
             - Agv.STRAIGHT: No direction change (straight line).
             - Agv.RIGHT: Turn right.
             - Agv.LEFT: Turn left.
             - Agv.REVERSE: Turn around (180 degrees).
    """
    direction_to_current = get_direction(prev_node, current_node)
    direction_to_next = get_direction(current_node, next_node)

    if direction_to_current is None or direction_to_next is None:
        return GO_STRAIGHT  # Default to GO_STRAIGHT if direction data is missing

    if direction_to_current == direction_to_next:
        return GO_STRAIGHT  # No direction change

    # Maps to determine action based on direction transitions
    # Format: {current_direction: {next_direction: action}}
    direction_actions = {
        NORTH: {
            EAST: TURN_RIGHT,
            WEST: TURN_LEFT,
            SOUTH: TURN_AROUND
        },
        EAST: {
            SOUTH: TURN_RIGHT,
            NORTH: TURN_LEFT,
            WEST: TURN_AROUND
        },
        SOUTH: {
            WEST: TURN_RIGHT,
            EAST: TURN_LEFT,
            NORTH: TURN_AROUND
        },
        WEST: {
            NORTH: TURN_RIGHT,
            SOUTH: TURN_LEFT,
            EAST: TURN_AROUND
        }
    }

    # Get the action from the direction maps, default to GO_STRAIGHT if not found
    return direction_actions.get(direction_to_current, {}).get(direction_to_next, GO_STRAIGHT)


def format_instruction_set(path):
    """
    Generate the initial path for a given path.

    Args:
        path (list): A list of nodes representing the path.

    Returns:
        list: A list of tuples representing the initial path for the path.
              Each tuple is in the format (from_node, to_node, action).
    """
    if len(path) < 2:
        return []

    initial_path = []
    for i in range(1, len(path) - 1):
        prev_node = path[i - 1]
        current_node = path[i]
        next_node = path[i + 1]
        action = get_action(prev_node, current_node, next_node)
        initial_path.append((prev_node, current_node, action))

    # Add the final segment to the initial path
    # We're using STRAIGHT as a default action for the final node
    # This could be modified to use a dedicated STOP constant if available in the future
    initial_path.append((path[-2], path[-1], GO_STRAIGHT))
    return initial_path
