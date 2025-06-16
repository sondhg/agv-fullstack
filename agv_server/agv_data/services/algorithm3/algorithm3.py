from ...models import Agv
import logging

logger = logging.getLogger(__name__)


class DeadlockResolver:
    """
    Algorithm 3: Deadlock Detection and Resolution

    This class implements deadlock detection and resolution strategies for AGVs
    following the DSPA algorithm approach.
    """

    def __init__(self, agv: Agv):
        self.agv = agv

    # === Public Interface ===
    def has_heading_on_deadlock(self) -> bool:
        """Check if this AGV is in a head-on deadlock situation."""
        return self._find_deadlocked_agv_in_head_on() is not None

    def has_loop_deadlock(self) -> bool:
        """Check if this AGV is part of a loop deadlock."""
        return self._detect_loop_deadlock()

    def resolve_heading_on_deadlock(self):
        """Resolve head-on deadlock based on spare_flag priority."""
        other_agv = self._find_deadlocked_agv_in_head_on()
        if not other_agv:
            return

        if self.agv.spare_flag:
            # This AGV moves to backup, other AGV moves normally
            self._move_to_backup_node(self.agv, other_agv.agv_id)
            self._move_to_next_node(other_agv)
        else:
            # Other AGV moves to backup, this AGV moves normally
            self._move_to_backup_node(other_agv, self.agv.agv_id)
            self._move_to_next_node(self.agv)

    def resolve_loop_deadlock(self):
        """Resolve loop deadlock (implementation depends on specific strategy)."""
        # For now, just reserve current position
        # This can be extended with more sophisticated loop breaking logic
        self.reserve_current_position()

    def reserve_current_position(self):
        """Reserve the current position of the AGV."""
        self.agv.reserved_node = self.agv.current_node
        self.agv.save(update_fields=['reserved_node'])

    def clear_deadlock_resolution_state(self):
        """Clear deadlock resolution tracking state."""
        self.agv.waiting_for_deadlock_resolution = False
        self.agv.deadlock_partner_agv_id = None
        self.agv.save(
            update_fields=['waiting_for_deadlock_resolution', 'deadlock_partner_agv_id'])

    # === Private Implementation ===

    def _find_deadlocked_agv_in_head_on(self) -> Agv:
        """
        Find the other AGV in a head-on deadlock with this AGV.

        Head-on deadlock occurs when:
        - AGV A's next_node is AGV B's current_node
        - AGV B's next_node is AGV A's current_node

        Returns:
            Agv: The other AGV in deadlock, or None if no deadlock exists
        """
        other_agvs = Agv.objects.exclude(agv_id=self.agv.agv_id)

        for other_agv in other_agvs:
            if (self.agv.next_node == other_agv.current_node and
                    self.agv.current_node == other_agv.next_node):
                return other_agv

        return None

    def _detect_loop_deadlock(self) -> bool:
        """
        Detect if this AGV is part of a loop deadlock.

        A loop deadlock exists when there's a cycle where each AGV's next_node
        is another AGV's current_node, forming a closed loop.

        Returns:
            bool: True if loop deadlock is detected
        """
        return self._find_deadlock_cycle(self.agv, set())

    def _find_deadlock_cycle(self, start_agv: Agv, visited: set) -> bool:
        """
        Recursively search for deadlock cycles starting from the given AGV.

        Args:
            start_agv: AGV to start the cycle detection from
            visited: Set of already visited AGV IDs

        Returns:
            bool: True if a cycle is found
        """
        if start_agv.agv_id in visited:
            return True  # Cycle detected

        # Find AGVs whose current_node matches this AGV's next_node
        visited.add(start_agv.agv_id)
        potential_next_agvs = Agv.objects.filter(
            current_node=start_agv.next_node
        ).exclude(agv_id=start_agv.agv_id)

        for next_agv in potential_next_agvs:
            if self._find_deadlock_cycle(next_agv, visited.copy()):
                return True

        return False

    def _move_to_backup_node(self, agv: Agv, partner_agv_id: int):
        """
        Move AGV to its backup node to resolve deadlock.

        This creates a temporary detour path: backup_node -> current_node -> original_path

        Args:
            agv: The AGV to move to backup node
            partner_agv_id: ID of the AGV that this AGV had deadlock with
        """
        current_node_str = str(agv.current_node)

        if current_node_str not in agv.backup_nodes:
            logger.warning(
                f"No backup node available for AGV {agv.agv_id} at node {agv.current_node}")
            return

        backup_node = agv.backup_nodes[current_node_str]

        logger.info(
            f"Moving AGV {agv.agv_id} to backup node {backup_node} to resolve deadlock")

        # Create detour path: backup_node -> current_node -> remaining_path
        new_path = [backup_node, agv.current_node] + agv.remaining_path

        # Update AGV state for backup node movement and track deadlock resolution
        agv.remaining_path = new_path
        agv.next_node = backup_node
        agv.reserved_node = backup_node
        agv.motion_state = Agv.MOVING
        agv.waiting_for_deadlock_resolution = True
        agv.deadlock_partner_agv_id = partner_agv_id

        agv.save(update_fields=['remaining_path', 'next_node', 'reserved_node',
                                'motion_state', 'waiting_for_deadlock_resolution',
                                'deadlock_partner_agv_id'])

    def _move_to_next_node(self, agv: Agv):
        """Move AGV to its next node normally."""
        logger.info(f"Moving AGV {agv.agv_id} to next node {agv.next_node}")

        agv.motion_state = Agv.MOVING
        agv.reserved_node = agv.next_node
        agv.save(update_fields=['motion_state', 'reserved_node'])
