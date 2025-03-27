from map_data.models import Direction

# Define constants for cardinal directions
NORTH = 1
EAST = 2
SOUTH = 3
WEST = 4


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
        str: The action the AGV should take at the `current_node`:
             - "none": No direction change (straight line).
             - "right": Turn right.
             - "left": Turn left.
             - "reverse": Turn around (180 degrees).
    """
    direction_to_current = get_direction(prev_node, current_node)
    direction_to_next = get_direction(current_node, next_node)

    if direction_to_current is None or direction_to_next is None:
        return "none"  # Default to "none" if direction data is missing

    if direction_to_current == direction_to_next:
        return "none"  # No direction change (straight line)
    elif (direction_to_current == NORTH and direction_to_next == EAST) or \
         (direction_to_current == EAST and direction_to_next == SOUTH) or \
         (direction_to_current == SOUTH and direction_to_next == WEST) or \
         (direction_to_current == WEST and direction_to_next == NORTH):
        return "right"  # Clockwise turn
    elif (direction_to_current == NORTH and direction_to_next == WEST) or \
         (direction_to_current == WEST and direction_to_next == SOUTH) or \
         (direction_to_current == SOUTH and direction_to_next == EAST) or \
         (direction_to_current == EAST and direction_to_next == NORTH):
        return "left"  # Counterclockwise turn
    elif (direction_to_current == NORTH and direction_to_next == SOUTH) or \
         (direction_to_current == SOUTH and direction_to_next == NORTH) or \
         (direction_to_current == EAST and direction_to_next == WEST) or \
         (direction_to_current == WEST and direction_to_next == EAST):
        return "reverse"  # Turn around (180 degrees)
    else:
        return "none"  # Default to "none" if 3 nodes are in a straight line


def format_instruction_set(path):
    """
    Generate the instruction set for a given path.

    Args:
        path (list): A list of nodes representing the path.

    Returns:
        list: A list of tuples representing the instruction set for the path.
              Each tuple is in the format (from_node, to_node, action).
    """
    instruction_set = []
    for i in range(1, len(path) - 1):
        prev_node = path[i - 1]
        current_node = path[i]
        next_node = path[i + 1]
        action = get_action(prev_node, current_node, next_node)
        instruction_set.append((prev_node, current_node, action))

    # Add the final segment to the instruction set
    instruction_set.append((path[-2], path[-1], "stop"))
    return instruction_set
