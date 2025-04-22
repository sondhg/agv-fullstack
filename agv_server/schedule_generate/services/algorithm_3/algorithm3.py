"""
Implementation of Algorithm 3: Deadlock Resolution of the Central Controller
"""
from typing import Dict, List, Optional, Tuple
from django.db import transaction
from agv_data.models import Agv
from schedule_generate.constants import AGVState


class DeadlockResolver:
    """
    Implements Algorithm 3: Deadlock Resolution of the Central Controller.

    This class detects and resolves deadlocks between AGVs using the DSPA algorithm.
    It identifies deadlock situations and directs AGVs to move to their spare points 
    to resolve the deadlocks.
    """

    def __init__(self):
        """Initialize the Deadlock Resolver."""
        pass

    def detect_and_resolve_deadlocks(self) -> Dict:
        """
        Detect and resolve any deadlocks in the system.
        This implements the main logic of Algorithm 3 from the research paper.

        Returns:
            Dict: Result of deadlock detection and resolution
                {
                    "success": bool,         # Whether the operation was successful
                    "message": str,          # Description of the operation result
                    "deadlocks_resolved": int,  # Number of deadlocks resolved
                    "agvs_moved": List[int]  # List of AGV IDs that were moved to resolve deadlocks
                }
        """
        try:
            # Get all AGVs that are in WAITING state
            waiting_agvs = Agv.objects.filter(motion_state=AGVState.WAITING)

            if not waiting_agvs:
                return {
                    "success": True,
                    "message": "No AGVs in waiting state, no deadlocks to check",
                    "deadlocks_resolved": 0,
                    "agvs_moved": []
                }

            # Keep track of resolved deadlocks and moved AGVs
            deadlocks_resolved = 0
            agvs_moved = []

            # Check for head-on deadlocks
            head_on_deadlocks = self._detect_head_on_deadlocks(waiting_agvs)
            for agv1, agv2 in head_on_deadlocks:
                # Resolve the head-on deadlock
                resolved, moved_agv = self._resolve_head_on_deadlock(
                    agv1, agv2)
                if resolved:
                    deadlocks_resolved += 1
                    agvs_moved.append(moved_agv.agv_id)

            # Check for loop deadlocks
            loop_deadlocks = self._detect_loop_deadlocks(waiting_agvs)
            for deadlock_agvs in loop_deadlocks:
                # Resolve the loop deadlock
                resolved, moved_agv = self._resolve_loop_deadlock(
                    deadlock_agvs)
                if resolved:
                    deadlocks_resolved += 1
                    agvs_moved.append(moved_agv.agv_id)

            if deadlocks_resolved > 0:
                return {
                    "success": True,
                    "message": f"Successfully resolved {deadlocks_resolved} deadlocks",
                    "deadlocks_resolved": deadlocks_resolved,
                    "agvs_moved": agvs_moved
                }
            else:
                return {
                    "success": True,
                    "message": "No deadlocks detected",
                    "deadlocks_resolved": 0,
                    "agvs_moved": []
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error detecting or resolving deadlocks: {str(e)}",
                "deadlocks_resolved": 0,
                "agvs_moved": []
            }

    def _detect_head_on_deadlocks(self, waiting_agvs) -> List[Tuple[Agv, Agv]]:
        """
        Detect head-on deadlocks between AGVs.
        A head-on deadlock occurs when v_n^i = v_c^j and v_n^j = v_c^i.

        Args:
            waiting_agvs: QuerySet of AGVs in waiting state

        Returns:
            List[Tuple[Agv, Agv]]: List of pairs of AGVs in head-on deadlock
        """
        deadlocks = []

        for agv1 in waiting_agvs:
            if not agv1.next_node:
                continue

            for agv2 in waiting_agvs:
                # Skip self comparison
                if agv1.agv_id == agv2.agv_id or not agv2.next_node:
                    continue

                # Check for head-on deadlock condition from Definition 9
                # v_n^i = v_c^j and v_n^j = v_c^i
                if (agv1.next_node == agv2.current_node and
                        agv2.next_node == agv1.current_node):
                    deadlocks.append((agv1, agv2))

        return deadlocks

    def _detect_loop_deadlocks(self, waiting_agvs) -> List[List[Agv]]:
        """
        Detect loop deadlocks among AGVs.
        A loop deadlock occurs when a set of vehicles forms a closed loop
        such that v_n^i = v_c^j, v_n^j = v_c^k, ..., v_n^m = v_c^i.

        Args:
            waiting_agvs: QuerySet of AGVs in waiting state

        Returns:
            List[List[Agv]]: List of groups of AGVs in loop deadlock
        """
        # Create a directed graph where edges represent "wants to move to"
        graph = {}
        # Map node to AGV for easy lookup
        node_to_agv = {}

        for agv in waiting_agvs:
            if not agv.next_node:
                continue

            graph[agv.current_node] = agv.next_node
            node_to_agv[agv.current_node] = agv

        # Find cycles in the graph (loop deadlocks)
        deadlocks = []
        visited = set()

        for node in graph:
            if node in visited:
                continue

            # DFS to detect cycles
            path = []
            cycle = self._find_cycle(graph, node, visited, path)
            if cycle and len(cycle) > 1:  # Ensure it's a genuine cycle with multiple AGVs
                # Convert node cycle to AGV list
                agv_cycle = [node_to_agv[node]
                             for node in cycle if node in node_to_agv]
                if len(agv_cycle) > 1:  # Make sure we have at least 2 AGVs
                    deadlocks.append(agv_cycle)

        return deadlocks

    def _find_cycle(self, graph, node, visited, path):
        """
        Helper function to find cycles in a directed graph using DFS.

        Args:
            graph: Dictionary representing the directed graph
            node: Current node being examined
            visited: Set of already visited nodes
            path: Current path being explored

        Returns:
            List or None: The cycle if found, None otherwise
        """
        if node in path:
            # Found a cycle, return the cycle portion of the path
            start_index = path.index(node)
            return path[start_index:]

        if node in visited or node not in graph:
            return None

        visited.add(node)
        path.append(node)

        # Visit the next node
        next_node = graph[node]
        cycle = self._find_cycle(graph, next_node, visited, path)

        path.pop()  # Remove the current node from the path

        return cycle

    @transaction.atomic
    def _resolve_head_on_deadlock(self, agv1: Agv, agv2: Agv) -> Tuple[bool, Optional[Agv]]:
        """
        Resolve a head-on deadlock between two AGVs as described in Algorithm 3 lines 5-12.

        One AGV with spare points moves to its spare point, allowing the other AGV to proceed.

        Args:
            agv1: First AGV in the deadlock
            agv2: Second AGV in the deadlock

        Returns:
            Tuple[bool, Optional[Agv]]: (resolved, moved_agv)
                - resolved: Whether the deadlock was successfully resolved
                - moved_agv: The AGV that was moved to a spare point
        """
        if agv1.spare_flag:
            # AGV1 has spare points, move it to spare point
            return self._move_to_spare_point(agv1, agv2)
        elif agv2.spare_flag:
            # AGV2 has spare points, move it to spare point
            return self._move_to_spare_point(agv2, agv1)
        else:
            # Neither AGV has spare points, deadlock cannot be resolved
            return False, None

    @transaction.atomic
    def _resolve_loop_deadlock(self, deadlock_agvs: List[Agv]) -> Tuple[bool, Optional[Agv]]:
        """
        Resolve a loop deadlock among a set of AGVs as described in Algorithm 3 lines 13-17.

        Select one AGV with spare points to move to its spare point, allowing others to proceed.

        Args:
            deadlock_agvs: List of AGVs involved in the loop deadlock

        Returns:
            Tuple[bool, Optional[Agv]]: (resolved, moved_agv)
                - resolved: Whether the deadlock was successfully resolved
                - moved_agv: The AGV that was moved to a spare point
        """
        # Find an AGV with spare points
        for agv in deadlock_agvs:
            if agv.spare_flag:
                # Find the next AGV in the loop
                for other_agv in deadlock_agvs:
                    if other_agv.agv_id != agv.agv_id and other_agv.next_node == agv.current_node:
                        # Move AGV to spare point, let other proceed
                        return self._move_to_spare_point(agv, other_agv)

        # No AGV has spare points, deadlock cannot be resolved
        return False, None

    @transaction.atomic
    def _move_to_spare_point(self, agv_to_move: Agv, agv_to_proceed: Agv) -> Tuple[bool, Optional[Agv]]:
        """
        Move an AGV to its spare point and let another AGV proceed.

        According to Example 3 in algorithms-pseudocode.tex, when an AGV moves to a spare point,
        its residual path should be updated to include the spare point followed by its current path.
        For example: Π_3 = {6, 14, 13, 12, 11, 19} after r_3 moves to spare point 6.

        Args:
            agv_to_move: AGV to move to spare point
            agv_to_proceed: AGV that will proceed to its next node

        Returns:
            Tuple[bool, Agv]: (success, moved_agv)
                - success: Whether the operation was successful
                - moved_agv: The AGV that was moved (if successful)
        """
        try:
            # Get the current node as a string since spare_points keys are stored as strings
            current_node_str = str(agv_to_move.current_node)

            # Check if there's a spare point for the current node
            if not agv_to_move.spare_points or current_node_str not in agv_to_move.spare_points:
                return False, None

            # Get the spare point
            spare_point = agv_to_move.spare_points[current_node_str]

            # AGV moves to spare point - modify residual path to include the spare point
            if agv_to_move.active_schedule:
                # Create the correct residual path according to Example 3 in algorithms-pseudocode.tex
                # The residual path should be [spare_point, current_node, ...rest of original path]
                # Example: Π_3 = {6, 14, 13, 12, 11, 19}
                residual_path = agv_to_move.active_schedule.residual_path

                # First, create a new residual path starting with the spare point
                new_residual_path = [spare_point]

                # Then add the current node if it's not already in the new path
                if agv_to_move.current_node != spare_point:
                    new_residual_path.append(agv_to_move.current_node)

                # Now add the rest of the original path, excluding the current node if it's there
                # (since we already added it above)
                original_path_rest = []
                if agv_to_move.current_node in residual_path:
                    # Find the index of the current node in the residual path
                    current_index = residual_path.index(
                        agv_to_move.current_node)
                    # Get the remainder of the path after the current node
                    original_path_rest = residual_path[current_index + 1:]
                else:
                    # If current node is not in residual path, keep the whole original path
                    original_path_rest = residual_path

                # Combine the parts
                new_residual_path.extend(original_path_rest)

                # Update the residual path
                agv_to_move.active_schedule.residual_path = new_residual_path
                agv_to_move.active_schedule.save()

                # Update AGV state and node information
                agv_to_move.next_node = spare_point
                agv_to_move.reserved_node = spare_point
                agv_to_move.motion_state = AGVState.MOVING
                agv_to_move.save()

                # Update the proceeding AGV state
                agv_to_proceed.motion_state = AGVState.MOVING
                agv_to_proceed.reserved_node = agv_to_proceed.next_node
                agv_to_proceed.save()

                return True, agv_to_move

            return False, None

        except Exception as e:
            # Log the error
            print(f"Error moving AGV to spare point: {str(e)}")
            return False, None
