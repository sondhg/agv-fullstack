from ...models import Agv
import logging

logger = logging.getLogger(__name__)


class ControlPolicy:
    """
    Algorithm 2: DSPA Control Policy

    This class implements the control policy that determines how AGVs should move
    based on their current state and the state of other AGVs in the system.
    """

    def __init__(self, agv: Agv):
        self.agv = agv

    # === Position and Path Updates ===

    def update_position_info(self, current_node):
        """
        Update all position-related information when AGV reaches a new node.

        Args:
            current_node (int): The new current position of the AGV
        """
        self._update_node_positions(current_node)
        self._update_path_info(current_node)
        self._update_shared_nodes(current_node)

    def _update_node_positions(self, current_node):
        """Update current and previous node positions."""
        if self.agv.current_node is not None:
            self.agv.previous_node = self.agv.current_node

        self.agv.current_node = current_node
        self.agv.save(update_fields=['current_node', 'previous_node'])

    def _update_path_info(self, current_node):
        """Update remaining path and next node based on current position."""
        # Remove current node from remaining path if it matches
        if (self.agv.remaining_path and
            len(self.agv.remaining_path) > 0 and
                current_node == self.agv.remaining_path[0]):

            logger.debug(
                f"AGV {self.agv.agv_id} reached node {current_node}, removing from remaining path")
            self.agv.remaining_path = self.agv.remaining_path[1:]
            self.agv.save(update_fields=['remaining_path'])

        # Check for journey phase transition after updating remaining path
        self._check_journey_phase_transition(current_node)

        # Update next node based on remaining path
        if self.agv.remaining_path and len(self.agv.remaining_path) > 0:
            self.agv.next_node = self.agv.remaining_path[0]
            self.agv.save(update_fields=['next_node'])
        else:
            # Clear next_node if no remaining path
            logger.debug(
                f"AGV {self.agv.agv_id} has no remaining path, clearing next_node")
            self.agv.next_node = None
            self.agv.save(update_fields=['next_node'])

    def _update_shared_nodes(self, current_node):
        """Update common nodes and adjacent common nodes when reaching a node."""
        self._remove_from_shared_nodes(current_node, 'common_nodes')
        self._remove_from_shared_nodes(current_node, 'adjacent_common_nodes')
        self._cleanup_insufficient_adjacent_nodes()

    def _remove_from_shared_nodes(self, node, field_name):
        """Remove node from shared node lists of this and other AGVs if appropriate."""
        # Remove from this AGV's list
        shared_nodes = getattr(self.agv, field_name)
        if node in shared_nodes:
            shared_nodes.remove(node)
            setattr(self.agv, field_name, shared_nodes)
            self.agv.save(update_fields=[field_name])

        # Check other AGVs with this node in their shared nodes
        filter_kwargs = {f"{field_name}__contains": [node]}
        other_agvs_with_node = Agv.objects.filter(
            **filter_kwargs).exclude(agv_id=self.agv.agv_id)

        # If only one or no other AGV has this node, remove it from them too
        if other_agvs_with_node.count() <= 1:
            for other_agv in other_agvs_with_node:
                other_shared_nodes = getattr(other_agv, field_name)
                if node in other_shared_nodes:
                    other_shared_nodes.remove(node)
                    setattr(other_agv, field_name, other_shared_nodes)
                    other_agv.save(update_fields=[field_name])

    def _cleanup_insufficient_adjacent_nodes(self):
        """Clear adjacent_common_nodes for all AGVs if they have less than 2 nodes."""
        for agv in Agv.objects.all():
            if len(agv.adjacent_common_nodes) < 2:
                agv.adjacent_common_nodes = []
                agv.save(update_fields=['adjacent_common_nodes'])

    def _check_journey_phase_transition(self, current_node):
        """
        Check if the AGV has completed its outbound journey and should transition to inbound journey,
        or if it has completed the entire order journey.
        """
        # Only check transition if AGV has an active order
        if not self.agv.active_order:
            return

        # Handle outbound to inbound transition
        if self.agv.journey_phase == Agv.OUTBOUND:
            workstation_node = self.agv.active_order.workstation_node

            # If AGV has reached workstation and outbound journey is complete
            if current_node == workstation_node and self._is_outbound_journey_complete():
                self._transition_to_inbound_journey()

        # Handle order completion on inbound journey
        elif self.agv.journey_phase == Agv.INBOUND:
            # ADDITIONAL CHECK: Fix remaining path if AGV is already in inbound phase
            # but remaining path wasn't properly updated during transition
            self._validate_inbound_remaining_path(current_node)

            parking_node = self.agv.active_order.parking_node

            # If AGV has reached parking node and inbound journey is complete
            if current_node == parking_node and self._is_inbound_journey_complete():
                self._complete_order_journey()

    def _is_inbound_journey_complete(self):
        """
        Check if the inbound journey is complete.
        Returns True if:
        1. The remaining path is empty (reached parking node), OR
        2. AGV is at the parking node (last node of inbound path)
        """
        # If no remaining path, inbound journey is complete
        if not self.agv.remaining_path or len(self.agv.remaining_path) == 0:
            return True

        # Check if AGV has reached the parking node (last node of inbound path)
        if (self.agv.active_order and
                self.agv.current_node == self.agv.active_order.parking_node):
            return True

        return False

    def _validate_inbound_remaining_path(self, current_node):
        """
        Validate and fix the remaining path for AGVs already in inbound phase.
        This handles cases where AGV is in inbound phase but remaining path wasn't properly updated.
        """
        if not self.agv.inbound_path:
            return

        # Special case: If AGV is at the parking node (end of inbound journey), clear remaining path
        if (self.agv.active_order and
                current_node == self.agv.active_order.parking_node):

            if self.agv.remaining_path:
                logger.info(
                    f"AGV {self.agv.agv_id} has reached parking node {current_node}, clearing remaining path for order completion")
                self.agv.remaining_path = []
                self.agv.next_node = None
                self.agv.reserved_node = None
                self.agv.save(
                    update_fields=['remaining_path', 'next_node', 'reserved_node'])
            return

        # Check if remaining path needs correction for AGVs not at parking node
        should_fix = False

        # Case 1: Remaining path doesn't match inbound path structure
        if not self.agv.remaining_path:
            logger.warning(
                f"AGV {self.agv.agv_id} in inbound phase but has no remaining path")
            should_fix = True
        elif (len(self.agv.remaining_path) > len(self.agv.inbound_path) or
              not self._is_valid_inbound_remaining_path()):
            logger.warning(
                f"AGV {self.agv.agv_id} in inbound phase but remaining path doesn't match inbound structure")
            should_fix = True

        if should_fix:
            logger.info(
                f"Fixing remaining path for AGV {self.agv.agv_id} in inbound phase")

            # Set remaining path to inbound path
            self.agv.remaining_path = self.agv.inbound_path.copy()

            # Remove current node if it's at the start of the path
            if (self.agv.remaining_path and
                len(self.agv.remaining_path) > 0 and
                    current_node == self.agv.remaining_path[0]):

                logger.info(
                    f"AGV {self.agv.agv_id} is at node {current_node}, removing from remaining path")
                self.agv.remaining_path = self.agv.remaining_path[1:]

            # Update next_node
            if self.agv.remaining_path and len(self.agv.remaining_path) > 0:
                self.agv.next_node = self.agv.remaining_path[0]
            else:
                self.agv.next_node = None

            # Clear reserved_node
            self.agv.reserved_node = None

            # Save changes
            self.agv.save(
                update_fields=['remaining_path', 'next_node', 'reserved_node'])

            logger.info(
                f"Fixed AGV {self.agv.agv_id} remaining path: {self.agv.remaining_path}")

    def _is_valid_inbound_remaining_path(self):
        """Check if the current remaining path is a valid subset of the inbound path."""
        if not self.agv.inbound_path or not self.agv.remaining_path:
            return False

        # Find where remaining path should start in inbound path
        for i in range(len(self.agv.inbound_path)):
            if (len(self.agv.remaining_path) <= len(self.agv.inbound_path) - i and
                    self.agv.remaining_path == self.agv.inbound_path[i:i + len(self.agv.remaining_path)]):
                return True
        return False

    def _is_outbound_journey_complete(self):
        """
        Check if the outbound journey is complete.
        Returns True if the remaining path matches the inbound path or if remaining path is empty
        and we're at the workstation.
        """
        # If no remaining path, outbound journey is complete
        if not self.agv.remaining_path or len(self.agv.remaining_path) == 0:
            logger.debug(
                f"AGV {self.agv.agv_id} outbound journey complete: no remaining path")
            return True

        # If no inbound path is set, this is an error - log it but allow completion
        if not self.agv.inbound_path:
            logger.warning(
                f"AGV {self.agv.agv_id} has no inbound path set, treating outbound as complete")
            return True

        # If remaining path matches inbound path, outbound journey is complete
        if self.agv.remaining_path == self.agv.inbound_path:
            logger.debug(
                f"AGV {self.agv.agv_id} outbound journey complete: remaining path matches inbound path")
            return True

        # If current remaining path is a subset starting from the inbound path
        # This handles cases where remaining_path contains both outbound and inbound segments
        if (len(self.agv.remaining_path) <= len(self.agv.inbound_path) and
                self.agv.remaining_path == self.agv.inbound_path[:len(self.agv.remaining_path)]):
            logger.debug(
                f"AGV {self.agv.agv_id} outbound journey complete: remaining path is subset of inbound path")
            return True

        logger.debug(
            f"AGV {self.agv.agv_id} outbound journey not complete. Remaining: {self.agv.remaining_path}, Inbound: {self.agv.inbound_path}")
        return False

    def _transition_to_inbound_journey(self):
        """
        Transition AGV from outbound to inbound journey phase.
        Updates journey_phase and sets remaining_path to inbound_path.
        """
        logger.info(
            f"AGV {self.agv.agv_id} transitioning from outbound to inbound journey")

        # Validate that inbound path exists
        if not self.agv.inbound_path:
            logger.error(
                f"AGV {self.agv.agv_id} cannot transition to inbound: no inbound path set")
            return

        # Update journey phase to inbound
        self.agv.journey_phase = Agv.INBOUND

        # Set remaining path to the inbound path
        self.agv.remaining_path = self.agv.inbound_path.copy()

        # CRITICAL FIX: If AGV is already at the workstation (first node of inbound path),
        # remove it from remaining path since the AGV is already there
        if (self.agv.remaining_path and
            len(self.agv.remaining_path) > 0 and
                self.agv.current_node == self.agv.remaining_path[0]):

            logger.info(
                f"AGV {self.agv.agv_id} is already at workstation node {self.agv.current_node}, removing from remaining path")
            self.agv.remaining_path = self.agv.remaining_path[1:]

        # Update next_node based on the new remaining path
        if self.agv.remaining_path and len(self.agv.remaining_path) > 0:
            self.agv.next_node = self.agv.remaining_path[0]
        else:
            self.agv.next_node = None

        # Clear reserved_node so it gets updated by the control policy
        # The control policy will set the correct reserved_node based on the new next_node
        self.agv.reserved_node = None

        # Save the changes
        self.agv.save(update_fields=[
                      'journey_phase', 'remaining_path', 'next_node', 'reserved_node'])

        logger.info(
            f"AGV {self.agv.agv_id} now on inbound journey with remaining path: {self.agv.remaining_path}")

        # Recalculate common nodes for all AGVs since this AGV's path has changed
        try:
            from ..algorithm1.common_nodes import recalculate_all_common_nodes
            recalculate_all_common_nodes(log_summary=True)
            logger.info(
                f"Recalculated common nodes after AGV {self.agv.agv_id} inbound transition")
        except Exception as e:
            logger.error(
                f"Failed to recalculate common nodes after inbound transition: {str(e)}")

    def _complete_order_journey(self):
        """
        Complete the AGV's order journey when it reaches the parking node on inbound journey.
        This clears the active order and resets the AGV to idle state.
        """
        if not self.agv.active_order:
            logger.warning(
                f"AGV {self.agv.agv_id} cannot complete journey: no active order")
            return

        order_id = self.agv.active_order.order_id
        logger.info(f"AGV {self.agv.agv_id} completing order {order_id}")

        # Clear order-related data
        self.agv.active_order = None
        self.agv.initial_path = []
        self.agv.remaining_path = []
        self.agv.outbound_path = []
        self.agv.inbound_path = []
        self.agv.common_nodes = []
        self.agv.adjacent_common_nodes = []

        # Reset journey phase to outbound for next order
        self.agv.journey_phase = Agv.OUTBOUND

        # Set AGV to idle state
        self.agv.motion_state = Agv.IDLE
        self.agv.next_node = None
        self.agv.reserved_node = None

        # Set direction to turn around when AGV finishes its inbound path at parking node
        self.agv.direction_change = Agv.TURN_AROUND

        # Clear deadlock-related flags and spare flag
        self.agv.spare_flag = False
        self.agv.backup_nodes = {}
        self.agv.waiting_for_deadlock_resolution = False
        self.agv.deadlock_partner_agv_id = None

        # Save all changes
        self.agv.save(update_fields=[
            'active_order', 'initial_path', 'remaining_path', 'outbound_path',
            'inbound_path', 'common_nodes', 'adjacent_common_nodes', 'journey_phase',
            'motion_state', 'next_node', 'reserved_node', 'direction_change', 'spare_flag', 'backup_nodes',
            'waiting_for_deadlock_resolution', 'deadlock_partner_agv_id'
        ])

        # Recalculate common nodes for all AGVs since this AGV is now idle
        try:
            from ..algorithm1.common_nodes import recalculate_all_common_nodes
            recalculate_all_common_nodes(log_summary=True)
            logger.info(
                f"Recalculated common nodes after AGV {self.agv.agv_id} order completion")
        except Exception as e:
            logger.error(
                f"Failed to recalculate common nodes after order completion: {str(e)}")

        logger.info(
            f"AGV {self.agv.agv_id} order {order_id} completion finished - now idle")

    # === Movement Decision Logic ===

    def can_move_freely(self):
        """
        Check if AGV can move without any restrictions.
        This covers movement conditions 1 and 2 from the original algorithm.
        """
        if not self.agv.next_node:
            return False

        reserved_nodes = self._get_reserved_nodes_by_others()

        # Condition 1: Next node not reserved and not in adjacent common nodes
        if (self.agv.next_node not in reserved_nodes and
                self.agv.next_node not in self.agv.adjacent_common_nodes):
            return True

        # Condition 2: Next node in adjacent common nodes but safe to move
        if (self.agv.next_node not in reserved_nodes and
                self.agv.next_node in self.agv.adjacent_common_nodes):

            reserved_by_non_spare = self._get_reserved_nodes_by_others(
                spare_flag=False)
            adjacent_nodes_blocked = any(
                node in reserved_by_non_spare
                for node in self.agv.adjacent_common_nodes
            )
            return not adjacent_nodes_blocked

        return False

    def should_use_backup_nodes(self):
        """Check if backup node handling is needed."""
        # If AGV has no next_node (idle), no backup nodes are needed
        if not self.agv.next_node:
            return False

        reserved_nodes = self._get_reserved_nodes_by_others()
        return self.agv.next_node not in reserved_nodes

    def can_move_with_backup(self):
        """Check if AGV can move after backup node allocation (condition 3)."""
        # If AGV has no next_node (idle), it cannot move with backup
        if not self.agv.next_node:
            return False

        if not self.agv.backup_nodes:
            return False

        reserved_nodes = self._get_reserved_nodes_by_others()
        reserved_by_non_spare = self._get_reserved_nodes_by_others(
            spare_flag=False)

        adjacent_nodes_blocked = any(
            node in reserved_by_non_spare
            for node in self.agv.adjacent_common_nodes
        )

        return (self.agv.next_node not in reserved_nodes and
                self.agv.next_node in self.agv.adjacent_common_nodes and
                adjacent_nodes_blocked)

    # === State Management ===

    def set_moving_state(self):
        """Set AGV to moving state without backup nodes."""
        self.agv.motion_state = Agv.MOVING
        self.agv.spare_flag = False
        self.agv.backup_nodes = {}
        self.agv.reserved_node = self.agv.next_node
        self.agv.save(
            update_fields=['motion_state', 'spare_flag', 'backup_nodes', 'reserved_node'])

    def set_moving_with_backup_state(self):
        """Set AGV to moving state with backup nodes."""
        self.agv.motion_state = Agv.MOVING
        self.agv.spare_flag = True
        self.agv.reserved_node = self.agv.next_node
        self.agv.save(update_fields=['motion_state',
                      'spare_flag', 'reserved_node'])

    def set_waiting_state(self):
        """Set AGV to waiting state."""
        self.agv.motion_state = Agv.WAITING
        self.agv.save(update_fields=['motion_state'])

    # === Backup Node Management ===

    def cleanup_current_backup_node(self):
        """Remove backup node associated with current position."""
        if (self.agv.current_node is not None and
                str(self.agv.current_node) in self.agv.backup_nodes):

            backup_nodes_copy = dict(self.agv.backup_nodes)
            backup_nodes_copy.pop(str(self.agv.current_node))
            self.agv.backup_nodes = backup_nodes_copy
            self.agv.save(update_fields=['backup_nodes'])

    # === Helper Methods ===

    def _get_reserved_nodes_by_others(self, spare_flag=None):
        """
        Get reserved nodes from other AGVs, optionally filtered by spare_flag.

        Args:
            spare_flag (bool, optional): Filter by spare_flag value

        Returns:
            list: List of reserved nodes
        """
        other_agvs = Agv.objects.exclude(agv_id=self.agv.agv_id)

        if spare_flag is not None:
            other_agvs = other_agvs.filter(spare_flag=spare_flag)

        return [
            agv.reserved_node for agv in other_agvs
            if agv.reserved_node is not None
        ]
