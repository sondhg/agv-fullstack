from map_data.models import Direction
from ..models import Agv

# Extract cardinal direction constants directly from the Direction model
NORTH, EAST, SOUTH, WEST = (
    Direction.NORTH,
    Direction.EAST,
    Direction.SOUTH,
    Direction.WEST,
)
# Extract direction change constants directly from the Agv model
TURN_RIGHT, TURN_LEFT, GO_STRAIGHT, TURN_AROUND = (
    Agv.TURN_RIGHT,
    Agv.TURN_LEFT,
    Agv.GO_STRAIGHT,
    Agv.TURN_AROUND,
)


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
        # First try to get the direction with the exact node order
        return Direction.objects.get(node1=from_node, node2=to_node).direction
    except Direction.DoesNotExist:
        try:
            # If not found, try the reverse direction and map to opposite cardinal direction
            reverse_direction = Direction.objects.get(
                node1=to_node, node2=from_node
            ).direction
            # Map to opposite direction: NORTH<->SOUTH, EAST<->WEST
            direction_opposites = {NORTH: SOUTH, SOUTH: NORTH, EAST: WEST, WEST: EAST}
            return direction_opposites.get(reverse_direction)
        except Direction.DoesNotExist:
            return None  # Return None if no direction is found in either order


def get_action(previous_node, current_node, reserved_node):
    """
    Determine the action (direction change) based on three consecutive nodes.

    Args:
        previous_node (int): The previous node in the path.
        current_node (int): The current node in the path.
        reserved_node (int): The reserved node in the path.

    Returns:
        int: The action the AGV should take at the `current_node`:
             - Agv.STRAIGHT: No direction change (straight line).
             - Agv.RIGHT: Turn right.
             - Agv.LEFT: Turn left.
             - Agv.REVERSE: Turn around (180 degrees).
    """
    direction_from_previous_node_to_current_node = get_direction(
        previous_node, current_node
    )
    direction_from_current_node_to_reserved_node = get_direction(
        current_node, reserved_node
    )

    if (
        direction_from_previous_node_to_current_node is None
        or direction_from_current_node_to_reserved_node is None
    ):
        return GO_STRAIGHT  # Default to GO_STRAIGHT if direction data is missing

    if (
        direction_from_previous_node_to_current_node
        == direction_from_current_node_to_reserved_node
    ):
        return GO_STRAIGHT  # No direction change

    # Maps to determine action based on direction transitions
    # Format: {current_direction: {next_direction: action}}
    direction_actions = {
        NORTH: {EAST: TURN_RIGHT, WEST: TURN_LEFT, SOUTH: TURN_AROUND},
        EAST: {SOUTH: TURN_RIGHT, NORTH: TURN_LEFT, WEST: TURN_AROUND},
        SOUTH: {WEST: TURN_RIGHT, EAST: TURN_LEFT, NORTH: TURN_AROUND},
        WEST: {NORTH: TURN_RIGHT, SOUTH: TURN_LEFT, EAST: TURN_AROUND},
    }

    # Get the action from the direction maps, default to GO_STRAIGHT if not found
    return direction_actions.get(direction_from_previous_node_to_current_node, {}).get(
        direction_from_current_node_to_reserved_node, GO_STRAIGHT
    )


def determine_direction_change(agv: Agv):
    direction_change = get_action(
        agv.previous_node, agv.current_node, agv.reserved_node
    )
    agv.direction_change = direction_change
    agv.save(update_fields=["direction_change"])
