from ...models import Agv
import logging

logger = logging.getLogger(__name__)


class DeadlockResolver():
    def __init__(self, agv: Agv):
        self.agv = agv

    def is_heading_on_deadlock_detected(self) -> bool:
        """
        Detect if this AGV is in a head-on deadlock situation with another AGV.

        A deadlock is detected when:
        - The next_node of this AGV is the current_node of another AGV
        - The current_node of this AGV is the next_node of that same other AGV

        Returns:
            bool: True if a head-on deadlock is detected, False otherwise
        """
        other_agvs = Agv.objects.exclude(agv_id=self.agv.agv_id)
        for other_agv in other_agvs:
            if (self.agv.next_node == other_agv.current_node and
                    self.agv.current_node == other_agv.next_node):
                return True
        return False

    def get_deadlocked_agv_in_head_on_situation(self) -> Agv:
        """
        Get the other AGV that is in a head-on deadlock with this AGV.

        Returns:
            Agv: The other AGV in the deadlock, or None if no deadlock exists
        """
        other_agvs = Agv.objects.exclude(agv_id=self.agv.agv_id)
        for other_agv in other_agvs:
            if (self.agv.next_node == other_agv.current_node and
                    self.agv.current_node == other_agv.next_node):
                return other_agv
        return None

    def resolve_heading_on_deadlock(self):
        """
        Resolve head-on deadlock based on Algorithm 3 from the research paper.

        From the paper:
        If v_n^i = v_c^j and v_n^j = v_c^i (head-on deadlock detected):
            If F^i = 1 (this AGV has spare_flag = True):
                r_i moves to SP^i(v_c^i) (this AGV moves to its backup node)
                r_j moves to v_n^j (other AGV moves to its next node)
            Else:
                r_j moves to SP^j(v_c^j) (other AGV moves to its backup node)
                r_i moves to v_n^i (this AGV moves to its next node)
        """
        other_agv = self.get_deadlocked_agv_in_head_on_situation()
        if other_agv is None:
            return  # No deadlock to resolve
            # Determine which AGV should move to backup node based on spare_flag (F^i)
        if self.agv.spare_flag:
            # This AGV (r_i) has spare_flag=True, so it moves to backup node
            self._move_agv_to_backup_node(self.agv)
            # Other AGV (r_j) moves to its next node normally
            self._move_agv_to_next_node(other_agv)
        else:
            # Other AGV (r_j) should move to backup node
            self._move_agv_to_backup_node(other_agv)
            # This AGV (r_i) moves to its next node normally
            self._move_agv_to_next_node(self.agv)

    def _move_agv_to_backup_node(self, agv: Agv):
        """
        Move AGV to its backup node and update its path accordingly.
          According to the research paper, when an AGV moves to backup node:
        1. Set motion_state = MOVING
        2. Add the backup_node to the start of remaining_path
        3. Add the current_node as second element of remaining_path
        This allows the AGV to return to its main path later.
        """
        # Get the backup node for the current node
        current_node_str = str(agv.current_node)
        if current_node_str not in agv.backup_nodes:
            # No backup node available for current position
            logger.warning(
                f"No backup node available for AGV {agv.agv_id} at current node {agv.current_node}")
            return

        backup_node = agv.backup_nodes[current_node_str]
        logger.info(
            f"Moving AGV {agv.agv_id} to backup node {backup_node} from current node {agv.current_node}")

        # Update the remaining path: backup_node -> current_node -> rest of path
        new_remaining_path = [backup_node,
                              agv.current_node] + agv.remaining_path

        # Update AGV state
        agv.remaining_path = new_remaining_path
        # Next node is now the backup node
        agv.next_node = backup_node
        agv.reserved_node = backup_node
        agv.motion_state = Agv.MOVING

        # Save the updated AGV state
        agv.save(update_fields=['remaining_path',
                 'next_node', 'motion_state', 'reserved_node'])

    def _move_agv_to_next_node(self, agv: Agv):
        """
        Move AGV to its next node normally.
        """
        logger.info(
            f"Moving AGV {agv.agv_id} to its next node {agv.next_node}")
        agv.motion_state = Agv.MOVING
        agv.reserved_node = agv.next_node
        agv.save(update_fields=['motion_state', 'reserved_node'])

    def is_loop_deadlock_detected(self) -> bool:
        """
        Detect if this AGV is in a loop deadlock situation.

        A loop deadlock is detected when:
        Exists a set of AGVs {r_i,r_j,...,r_n} such that:
        - The next_node of each AGV in the set is the current_node of the next AGV in the set: v_n^i = v_c^j, v_n^j = v_c^k, ..., v_n^n = v_c^i

        Returns:
            bool: True if a loop deadlock is detected, False otherwise
        """
        # Get all AGVs except the current one
        other_agvs = Agv.objects.exclude(agv_id=self.agv.agv_id)

        # Check for loop deadlocks
        def detect_loop(start_agv, current_agv, visited=None):
            if visited is None:
                visited = set()

            # Add the current AGV to the visited set
            visited.add(current_agv.agv_id)

            # Get the next node of the current AGV
            next_node = current_agv.next_node

            # Find AGVs whose current_node is the next_node of the current AGV
            potential_next_agvs = [
                agv for agv in other_agvs
                if agv.current_node == next_node and agv.agv_id != current_agv.agv_id
            ]

            # Check each potential next AGV in the chain
            for next_agv in potential_next_agvs:
                # If we find the starting AGV, we've detected a loop
                if next_agv.agv_id == start_agv.agv_id:
                    return True

                # If we haven't visited this AGV yet, continue the search
                if next_agv.agv_id not in visited:
                    if detect_loop(start_agv, next_agv, visited):
                        return True

            return False

        # Start the loop detection from the current AGV
        return detect_loop(self.agv, self.agv)

    def _set_reserved_node_as_current_node(self):
        """
        Set the reserved node of the AGV to its current node.
        This is used when the AGV is waiting and needs to reserve its current position.
        """
        self.agv.reserved_node = self.agv.current_node
        self.agv.save(update_fields=['reserved_node'])
